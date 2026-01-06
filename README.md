# Sales Intelligence Tool

AI-powered web scraping tool that analyzes company websites to identify internship opportunities and generate personalized outreach strategies.

## 🎯 What It Does

- Scrapes company websites (up to 5 pages: about, blog, products, careers, etc.)
- Uses OpenAI GPT-4 to analyze technical gaps and business needs
- Generates specific "Trojan Horse" project ideas that an intern could build in 48 hours
- Creates professional PDF reports for outreach
- Drafts personalized connection messages

## 🛠️ Tech Stack

- **Python** - Core application logic
- **Streamlit** - Interactive web interface
- **BeautifulSoup** - Web scraping and HTML parsing
- **OpenAI API** - AI-powered content analysis
- **FPDF** - PDF report generation

## 🚀 Setup

### Prerequisites
- Python 3.8+
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Installation

1. Clone the repository:
```bash
git clone https://github.com/marinasofia/sales-intelligence-tool.git
cd sales-intelligence-tool
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

4. Run the application:
```bash
streamlit run app.py
```

## 💡 Why I Built This

This project explores:
- Integration with external APIs (OpenAI)
- Web scraping best practices with error handling and retry logic
- Building interactive applications with Streamlit
- Secure credential management with environment variables

As someone interested in sales engineering and data analysis, I wanted to understand how AI could automate prospect research and personalized outreach.

## 📖 How to Use

1. Enter a company website URL
2. Wait 30-60 seconds while the tool analyzes multiple pages
3. Review the AI-generated project recommendations
4. Download the PDF report
5. Use the sidebar to draft a personalized outreach message

## ⚠️ Note

This tool uses the OpenAI API, which is a paid service. You'll need your own API key. New accounts receive $5 in free credits (enough for ~30-40 analyses).

## 👤 Author

**Marina Sofia Martin**
- Email: marinasofiaml@gmail.com
- LinkedIn: [linkedin.com/in/marinasofiaml](https://www.linkedin.com/in/marinasofiaml)
- GitHub: [github.com/marinasofia](https://github.com/marinasofia)

---

*Currently seeking Summer 2026 internships in Data Analysis, Sales Engineering, and Software Development.*
