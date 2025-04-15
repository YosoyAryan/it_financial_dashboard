import sys
import os
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from news_scraper.scraper import get_it_tech_news, get_exchange_rate

st.set_page_config(page_title="IT Sector Financial Dashboard", layout="wide")
st.title("📊 IT Sector Financial Dashboard")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📈 Financial Overview", "💱 Exchange Rates", "📰 IT & Tech News"])

# --- Static Data ---
companies = {
    # Indian IT Companies (INR)
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "Wipro": "WIPRO.NS",
    "HCL Tech": "HCLTECH.NS",
    "Tech Mahindra": "TECHM.NS",

    # U.S. Tech Giants (USD)
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Amazon": "AMZN",
    "Google (Alphabet)": "GOOGL",
    "Meta (Facebook)": "META",
    "NVIDIA": "NVDA",

    # Global Tech
    "SAP (Germany)": "SAP",         # EUR
    "ASML (Netherlands)": "ASML",   # USD
    "Samsung (Korea)": "005930.KS", # KRW
    "Sony (Japan)": "6758.T",       # JPY
    "Taiwan Semiconductor (TSMC)": "TSM"  # USD
}

company_currency = {
    "TCS": "INR", "Infosys": "INR", "Wipro": "INR", "HCL Tech": "INR", "Tech Mahindra": "INR",
    "Apple": "USD", "Microsoft": "USD", "Amazon": "USD", "Google (Alphabet)": "USD",
    "Meta (Facebook)": "USD", "NVIDIA": "USD",
    "SAP (Germany)": "EUR", "ASML (Netherlands)": "USD",
    "Samsung (Korea)": "KRW", "Sony (Japan)": "JPY",
    "Taiwan Semiconductor (TSMC)": "USD"
}

forex_pairs = {
    "USD/INR": ("USD", "INR"),
    "EUR/INR": ("EUR", "INR"),
    "JPY/INR": ("JPY", "INR"),
    "CHF/INR": ("CHF", "INR"),
    "KRW/INR": ("KRW", "INR")
}

# Pre-fetch conversion rates to INR
conversion_rates = {}
for cur in set(company_currency.values()):
    if cur != "INR":
        try:
            rate = get_exchange_rate(cur, "INR")
            conversion_rates[cur] = rate
        except:
            conversion_rates[cur] = None

# ========== FINANCIAL OVERVIEW TAB ==========
with tab1:
    st.sidebar.header("📁 Financial Filters")
    selected_companies = st.sidebar.multiselect("Select Companies", list(companies.keys()), default=["TCS", "Infosys"])
    start_date = st.sidebar.date_input("Start Date", datetime(2024, 1, 1))
    end_date = st.sidebar.date_input("End Date", datetime.today())

    combined_data = {}
    key_stats_rows = {}
    price_alerts = {}

    for company in selected_companies:
        ticker_symbol = companies[company]
        currency = company_currency.get(company, "INR")
        conversion_rate = 1 if currency == "INR" else conversion_rates.get(currency, None)

        if conversion_rate is None:
            st.warning(f"Skipping {company} — Unable to convert {currency} to INR.")
            continue

        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(start=start_date, end=end_date)

        if data.empty:
            st.warning(f"No data available for {company}")
            continue

        # Convert prices to INR
        data["Close"] *= conversion_rate
        data["Open"] *= conversion_rate
        data["High"] *= conversion_rate
        data["Low"] *= conversion_rate

        data["30MA"] = data["Close"].rolling(window=30).mean()
        data["Daily Return"] = data["Close"].pct_change()
        data["Volatility"] = data["Daily Return"].rolling(window=30).std()
        data["Company"] = company

        combined_data[company] = data

        latest = data.iloc[-1]
        key_stats_rows[company] = {
            "Company": company,
            "Latest Price (INR)": round(latest["Close"], 2),
            "Volume": int(latest["Volume"]),
            "30-Day MA": round(latest["30MA"], 2),
            "Daily Return": round(latest["Daily Return"], 4),
            "30-Day Volatility": round(latest["Volatility"], 4)
        }

        price_alerts[company] = price_alerts.get(company, 0) or st.sidebar.number_input(
            f"Set alert for {company} (INR)", min_value=0.0
        )

    if combined_data:
        st.subheader("📈 Closing Price Comparison (INR)")
        fig_close = go.Figure()
        for company, data in combined_data.items():
            fig_close.add_trace(go.Scatter(x=data.index, y=data["Close"], mode='lines', name=company))
        fig_close.update_layout(title="Closing Prices (INR)", xaxis_title="Date", yaxis_title="Price (INR)")
        st.plotly_chart(fig_close, use_container_width=True)

        st.subheader("📉 Daily Return Comparison")
        fig_return = go.Figure()
        for company, data in combined_data.items():
            fig_return.add_trace(go.Scatter(x=data.index, y=data["Daily Return"], mode='lines', name=company))
        fig_return.update_layout(title="Daily Returns", xaxis_title="Date", yaxis_title="Return")
        st.plotly_chart(fig_return, use_container_width=True)

        st.subheader("📉 Candlestick Chart (Sample: TCS)")
        tcs_data = combined_data.get('TCS', None)
        if tcs_data is not None:
            fig_candle = go.Figure(data=[go.Candlestick(x=tcs_data.index,
                                                        open=tcs_data['Open'],
                                                        high=tcs_data['High'],
                                                        low=tcs_data['Low'],
                                                        close=tcs_data['Close'])])
            fig_candle.update_layout(title="Candlestick Chart for TCS (INR)", xaxis_title="Date", yaxis_title="Price (INR)")
            st.plotly_chart(fig_candle)

        st.subheader("📊 30-Day Rolling Volatility Comparison")
        fig_volatility = go.Figure()
        for company, data in combined_data.items():
            fig_volatility.add_trace(go.Scatter(x=data.index, y=data["Volatility"], mode='lines', name=company))
        fig_volatility.update_layout(title="30-Day Volatility", xaxis_title="Date", yaxis_title="Volatility")
        st.plotly_chart(fig_volatility, use_container_width=True)

        st.subheader("📋 Key Stats (Latest)")
        stats_df = pd.DataFrame(key_stats_rows.values())
        st.dataframe(stats_df, use_container_width=True)

        for company, data in combined_data.items():
            st.download_button(f"📥 Download {company} Data", data.to_csv().encode('utf-8'), f"{company}_stock_data.csv", "text/csv")
    else:
        st.info("Please select at least one company with available data.")

    for company, data in combined_data.items():
        if data['Close'].iloc[-1] > price_alerts.get(company, 0):
            st.markdown(f"🚨 **Price Alert**: {company} has crossed your set threshold with a price of {data['Close'].iloc[-1]:.2f} INR")

# ========== EXCHANGE RATES TAB ==========
with tab2:
    st.sidebar.header("💱 Forex Filters")
    selected_pairs = st.sidebar.multiselect("Select Currency Pairs", list(forex_pairs.keys()), default=["USD/INR", "EUR/INR"])

    exchange_alerts = {}
    exchange_data = []

    for pair in selected_pairs:
        base, target = forex_pairs[pair]
        alert_threshold = st.sidebar.number_input(f"Set alert for {pair} (Rate)", min_value=0.0)
        exchange_alerts[pair] = alert_threshold

        try:
            rate = get_exchange_rate(base, target)
            if rate:
                exchange_data.append({
                    "Currency Pair": pair,
                    "Rate": round(rate, 4),
                    "Date": datetime.today().strftime("%Y-%m-%d"),
                    "Alert Threshold": alert_threshold,
                    "Alert Triggered": "🚨 Yes" if rate > alert_threshold else "No"
                })

                if rate > alert_threshold:
                    st.markdown(f"🚨 **Rate Alert**: {pair} has crossed your set threshold with a rate of {rate}")

        except Exception as e:
            st.error(f"Error fetching rate for {pair}: {e}")

    if exchange_data:
        df = pd.DataFrame(exchange_data)
        st.subheader("💱 Real-Time Exchange Rates")
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 Download Exchange Rates", df.to_csv(index=False).encode('utf-8'), "exchange_rates.csv", "text/csv")
    else:
        st.warning("No data found. Try selecting a different currency pair.")

# ========== NEWS TAB ==========
with tab3:
    st.subheader("📰 Latest IT & Tech News")
    try:
        news = get_it_tech_news()
        if news:
            news_df = pd.DataFrame(news)
            for item in news:
                st.markdown(f"**{item['title']}**  \n"
                            f"[Read more]({item['link']})  \n"
                            f"_Sentiment: {item['sentiment']}_  \n"
                            f"> {item['summary']}  \n")
                st.markdown("---")

            st.download_button("📥 Download News Data", news_df.to_csv(index=False).encode('utf-8'), "it_tech_news.csv", "text/csv")
        else:
            st.info("No news found.")
    except Exception as e:
        st.error(f"Error fetching news: {e}")
