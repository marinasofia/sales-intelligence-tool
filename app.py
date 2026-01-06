"""
Sales Intelligence Tool - Internship Opportunity Analyzer

This tool scrapes company websites and uses AI to identify technical gaps
that could be addressed through internship projects.

Architecture:
- Web Scraping: BeautifulSoup + requests with retry logic
- AI Analysis: OpenAI GPT-4o-mini with structured prompts
- Output: Streamlit UI + PDF reports

Author: Marina Sofia Martin
Email: marinasofiaml@gmail.com
Date: January 2026
"""

import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import re
from fpdf import FPDF
from urllib.parse import urljoin, urlparse
import time
from typing import Tuple, List, Optional

# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(
    page_title="Internship Intelligence Agent", 
    layout="wide", 
    page_icon="🎓"
)

# Configuration constants
MAX_RETRIES = 3
REQUEST_TIMEOUT = 10
SCRAPE_DELAY = 1  # Seconds between requests (be respectful to servers)
MAX_TEXT_PER_PAGE = 5000  # Increased from 3000
MAX_TOTAL_TEXT = 20000  # Increased from 12000

# ============================================================================
# WEB SCRAPING FUNCTIONS
# ============================================================================

def get_important_links(base_url: str, soup: BeautifulSoup) -> List[str]:
    """
    Finds important pages to scrape for better company understanding.
    
    Looks for: about, blog, mission, product, careers, team, pricing pages.
    Only returns links from the same domain to avoid external sites.
    
    Args:
        base_url: The main company URL
        soup: BeautifulSoup object of the main page
        
    Returns:
        List of URLs to scrape (max 5 for efficiency)
    """
    links = set()
    keywords = ['blog', 'about', 'mission', 'product', 'team', 'careers', 'pricing', 'features']
    domain = urlparse(base_url).netloc
    
    for a in soup.find_all('a', href=True):
        full_url = urljoin(base_url, a['href'])
        
        # Only include links from same domain
        if urlparse(full_url).netloc == domain:
            # Check if any keyword is in the URL
            if any(k in full_url.lower() for k in keywords):
                links.add(full_url)
    
    # Return top 5 links (prioritize 'about' and 'blog')
    sorted_links = sorted(links, key=lambda x: (
        'about' in x.lower(),
        'blog' in x.lower(),
        'product' in x.lower()
    ), reverse=True)
    
    return sorted_links[:5]


def scrape_page(url: str, retry_count: int = 0) -> Tuple[str, Optional[BeautifulSoup]]:
    """
    Scrapes text content from a URL with retry logic and error handling.
    
    Args:
        url: The webpage URL to scrape
        retry_count: Current retry attempt (for recursive retries)
        
    Returns:
        Tuple of (extracted_text, soup_object)
        Returns ("", None) if scraping fails after all retries
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        res = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        
        # Check if request was successful
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Remove script and style elements (they're not useful content)
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            # Extract text with better formatting
            text = soup.get_text(separator=" ", strip=True)
            
            # Clean up excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Limit text length but try to end at sentence boundary
            if len(text) > MAX_TEXT_PER_PAGE:
                text = text[:MAX_TEXT_PER_PAGE]
                # Try to cut at last period
                last_period = text.rfind('.')
                if last_period > MAX_TEXT_PER_PAGE * 0.8:  # If we find a period in last 20%
                    text = text[:last_period + 1]
            
            return text, soup
            
        elif res.status_code == 403:
            return f"[Access denied to {url}]", None
        elif res.status_code == 404:
            return f"[Page not found: {url}]", None
        else:
            return f"[Error {res.status_code} accessing {url}]", None
            
    except requests.Timeout:
        if retry_count < MAX_RETRIES:
            time.sleep(2 ** retry_count)  # Exponential backoff
            return scrape_page(url, retry_count + 1)
        return f"[Timeout accessing {url}]", None
        
    except requests.ConnectionError:
        return f"[Connection failed to {url}]", None
        
    except Exception as e:
        return f"[Unexpected error scraping {url}: {str(e)[:100]}]", None


# ============================================================================
# PDF GENERATION FUNCTIONS
# ============================================================================

def clean_text_for_pdf(text: str) -> str:
    """
    Cleans text for PDF generation by removing markdown and special characters.
    
    Args:
        text: Raw text with potential markdown formatting
        
    Returns:
        Cleaned text safe for PDF encoding
    """
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'#+\s?', '', text)  # Headers
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Links
    
    # Replace smart quotes and special characters
    replacements = {
        '\u2018': "'", '\u2019': "'",  # Smart single quotes
        '\u201c': '"', '\u201d': '"',  # Smart double quotes
        '\u2013': '-', '\u2014': '--',  # En/em dashes
        '\u2026': '...',  # Ellipsis
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    
    # Encode to latin-1 (PDF-safe), replacing problematic characters
    return text.encode('latin-1', 'replace').decode('latin-1')


def create_pdf(text: str, url: str) -> bytes:
    """
    Creates a professional PDF report from analysis text.
    
    Args:
        text: The analysis report text
        url: The company URL analyzed
        
    Returns:
        PDF file as bytes
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Internship Opportunity Analysis", ln=True, align='L')
    
    # Company URL
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, f"Target: {url}", ln=True, align='L')
    
    # Date
    from datetime import datetime
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%B %d, %Y')}", ln=True, align='L')
    
    pdf.ln(10)
    
    # Main content
    pdf.set_font("Arial", size=11)
    safe_text = clean_text_for_pdf(text)
    pdf.multi_cell(0, 7, safe_text)
    
    return pdf.output(dest='S').encode('latin-1', 'replace')


# ============================================================================
# AI ANALYSIS FUNCTION
# ============================================================================

def analyze_company(combined_text: str) -> str:
    """
    Sends scraped company data to OpenAI for analysis.
    
    Args:
        combined_text: All scraped text from company website
        
    Returns:
        AI-generated analysis report
        
    Raises:
        Exception: If OpenAI API call fails
    """
    prompt = f"""
You are a Senior Engineering Manager mentoring a student.
Analyze the scraped company data to propose a 'Trojan Horse' internship project.

CRITICAL RULES:
1. **Avoid Core Features**: If the company IS a dashboard, do not suggest building a dashboard. Suggest a *plugin*, *integration*, or *automation* for it.
2. **Check for Redundancy**: If the text says they "already do X," do not suggest X. Suggest "Better X" or "X for Mobile."
3. **Use Analogies**: Explain technical concepts simply.

OUTPUT FORMAT:
1. **What They Do**: (1 sentence simple explanation).

2. **The "Plugin" Opportunity**:
   - Identify a specific *integration* or *workflow* that seems missing or manual.
   - Example: "They have a dashboard, but no easy way to export to Slack."

3. **The Project Pitch**:
   - **Name**: (Catchy)
   - **The Value**: "This saves engineers 5 hours a week by..."
   - **The Blueprint**: 4-week execution plan.

4. **Sanity Check (Google Terms)**:
   - List 2 specific search terms the student should Google to check if this feature already exists (e.g., "PostHog Slack Integration").

DATA:
{combined_text[:MAX_TOTAL_TEXT]}
"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    
    return response.choices[0].message.content


# ============================================================================
# STREAMLIT UI
# ============================================================================

st.title("🎓 Internship Intelligence Agent")
st.markdown("### Find a project, understand the tech, and pitch it with confidence.")
st.markdown("---")

# Main input form
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    with st.form(key='audit_form'):
        url = st.text_input(
            "Enter Company URL:", 
            placeholder="https://linear.app", 
            value="",
            help="Enter the main company website URL"
        )
        submitted = st.form_submit_button("🔍 Find My Internship Project")

# ============================================================================
# MAIN EXECUTION LOGIC
# ============================================================================

if submitted:
    if not url:
        st.warning("⚠️ Please enter a URL.")
    elif not url.startswith(('http://', 'https://')):
        st.error("⚠️ URL must start with http:// or https://")
    else:
        # Progress tracking
        progress_bar = st.progress(0)
        status = st.empty()
        
        try:
            # Step 1: Scrape main page
            status.info(f"📖 Reading main page: {url}")
            progress_bar.progress(20)
            
            main_text, soup = scrape_page(url)
            
            if not main_text or main_text.startswith('['):
                st.error(f"❌ Could not access {url}. Please check the URL and try again.")
                st.stop()
            
            combined_text = f"HOME PAGE:\n{main_text}\n\n"
            
            # Step 2: Find and scrape important links
            if soup:
                status.info("🔍 Finding important pages...")
                progress_bar.progress(30)
                
                important_links = get_important_links(url, soup)
                
                if important_links:
                    st.info(f"📚 Found {len(important_links)} additional pages to analyze")
                    
                    for i, link in enumerate(important_links):
                        status.info(f"📖 Reading: {link}")
                        progress_bar.progress(30 + (i + 1) * (40 // len(important_links)))
                        
                        time.sleep(SCRAPE_DELAY)  # Be respectful to servers
                        
                        sub_text, _ = scrape_page(link)
                        if sub_text and not sub_text.startswith('['):
                            combined_text += f"PAGE ({link}):\n{sub_text}\n\n"
            
            # Step 3: AI Analysis
            status.info("🤖 Analyzing company data with AI...")
            progress_bar.progress(80)
            
            report = analyze_company(combined_text)
            
            # Save to session state
            st.session_state['report'] = report
            st.session_state['url'] = url
            
            # Complete
            progress_bar.progress(100)
            status.success("✅ Analysis complete!")
            time.sleep(1)
            status.empty()
            progress_bar.empty()
            
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            st.info("💡 Try refreshing the page and attempting again.")


# ============================================================================
# RESULTS DISPLAY
# ============================================================================

if 'report' in st.session_state:
    st.markdown("---")
    st.subheader("📝 Your Project & Study Plan")
    st.markdown(st.session_state['report'])
    st.divider()
    
    # PDF Download
    pdf_data = create_pdf(st.session_state['report'], st.session_state['url'])
    st.download_button(
        "📄 Download PDF Report",
        pdf_data,
        "Internship_Project_Analysis.pdf",
        "application/pdf",
        help="Download a PDF version to send to hiring managers"
    )


# ============================================================================
# SIDEBAR - OUTREACH ASSISTANT
# ============================================================================

with st.sidebar:
    st.header("📢 Outreach Assistant")
    
    style = st.radio(
        "Email Style:",
        ["Casual Connection Request", "Professional Cold Email"],
        help="Choose the tone for your outreach message"
    )
    
    if st.button("✍️ Draft Message"):
        if 'report' in st.session_state:
            with st.spinner("Drafting your message..."):
                try:
                    prompt = f"""Write a {style} based on this internship project analysis. 
                    
Keep it:
- Humble but confident
- Max 150 words
- Focused on the value you can bring
- Include a clear ask (coffee chat or quick call)

REPORT:
{st.session_state['report'][:2000]}
"""
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.8,
                    )
                    
                    st.success("✅ Message drafted!")
                    st.code(response.choices[0].message.content, language=None)
                    
                except Exception as e:
                    st.error(f"Error generating message: {str(e)}")
        else:
            st.warning("⚠️ Run analysis first!")
    
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Personalize the message with details from the company
    - Mention specific people if possible
    - Keep it under 150 words
    - Include a clear call-to-action
    """)
