
# IT Sector Financial Dashboard

![Screenshot 2025-04-15 164137](https://github.com/user-attachments/assets/74e7ca9e-23c5-4f82-a395-11f3ba93c406)
![Screenshot 2025-04-15 164228](https://github.com/user-attachments/assets/a271d8ec-e8e4-44ba-8beb-5899a7bc9070)
![Screenshot 2025-04-15 164311](https://github.com/user-attachments/assets/e7f08539-7188-4272-bc68-11b1f33ffa0a)

This is an interactive **Streamlit** web application designed to provide key financial metrics for the IT sector. The dashboard aggregates stock performance, exchange rates, and IT & Tech news with sentiment analysis to give a holistic view of market conditions.

## Features
- **Stock Performance**: Displays stock price charts for major IT companies (TCS, Infosys, Wipro, HCL Tech, Tech Mahindra).
- **Exchange Rates**: Fetches exchange rates for key pairs (USD/INR, EUR/INR, JPY/INR, CHF/INR).
- **IT & Tech News**: Scrapes the latest news articles related to IT and Tech, providing summaries and sentiment analysis.

## Installation

### Prerequisites

- Python 3.8+
- Virtual environment (Recommended)

### Steps to Install and Run

1. Clone the repository or download the project folder.
   
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # On Windows, use .venv\Scriptsctivate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download necessary NLTK corpora:
   ```bash
   python -m nltk.downloader punkt
   ```

5. Run the Streamlit app:
   ```bash
   streamlit run dashboard/app.py
   ```

6. Open the web app in your browser at `http://localhost:8501`.

## Project Structure

```
it_financial_dashboard/
├── dashboard/
│   └── app.py             # Main Streamlit app for displaying dashboard
├── news_scraper/
│   └── scraper.py         # News scraping and sentiment analysis code
├── requirements.txt       # List of dependencies
└── .venv/                 # Virtual environment (not committed to version control)
```

## Dependencies

- **Streamlit**: For building the interactive web dashboard.
- **yfinance**: For fetching stock data.
- **pandas**: For data manipulation.
- **requests**: For making HTTP requests to fetch exchange rates and news.
- **beautifulsoup4**: For parsing and scraping HTML data.
- **textblob**: For performing sentiment analysis on news summaries.
- **newspaper3k**: For extracting articles from URLs.
- **nltk**: For natural language processing tasks, like tokenization.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **exchangerate.host API** for providing free exchange rate data.
- **Streamlit** for easy-to-use data visualization tools.
- **yfinance** for providing stock market data.
- **TextBlob** for sentiment analysis.
