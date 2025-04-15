import sys
import os
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# Local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from news_scraper.scraper import get_it_tech_news, get_exchange_rate

st.set_page_config(page_title="IT Sector Financial Dashboard", layout="wide")
st.title("📊 IT Sector Financial Dashboard")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📈 Financial Overview", "💱 Exchange Rates", "📰 IT & Tech News"])

# --- Static Data ---
companies = {
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "Wipro": "WIPRO.NS",
    "HCL Tech": "HCLTECH.NS",
    "Tech Mahindra": "TECHM.NS"
}

forex_pairs = {
    "USD/INR": ("USD", "INR"),
    "EUR/INR": ("EUR", "INR"),
    "JPY/INR": ("JPY", "INR"),
    "CHF/INR": ("CHF", "INR")
}

# ========== FINANCIAL OVERVIEW TAB (Enhanced with additional graphs and alerts) ==========
with tab1:
    st.sidebar.header("📁 Financial Filters")
    selected_companies = st.sidebar.multiselect("Select Companies", list(companies.keys()), default=["TCS", "Infosys"])
    start_date = st.sidebar.date_input("Start Date", datetime(2024, 1, 1))
    end_date = st.sidebar.date_input("End Date", datetime.today())

    combined_data = {}
    key_stats_rows = []

    price_alerts = {}

    for company in selected_companies:
        ticker_symbol = companies[company]
        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(start=start_date, end=end_date)

        if data.empty:
            st.warning(f"No data available for {company}")
            continue

        data["30MA"] = data["Close"].rolling(window=30).mean()
        data["Daily Return"] = data["Close"].pct_change()
        data["Volatility"] = data["Daily Return"].rolling(window=30).std()
        data["Company"] = company

        combined_data[company] = data

        # Collect key stats
        latest = data.iloc[-1]
        key_stats_rows.append({
            "Company": company,
            "Latest Price": round(latest["Close"], 2),
            "Volume": int(latest["Volume"]),
            "30-Day MA": round(latest["30MA"], 2),
            "Daily Return": round(latest["Daily Return"], 4),
            "30-Day Volatility": round(latest["Volatility"], 4)
        })

        # Check if price crosses alert threshold
        price_alerts[company] = price_alerts.get(company, 0) or st.sidebar.number_input(f"Set alert for {company} (Price)", min_value=0.0)

    # ---- Plotting the charts ----
    if combined_data:
        st.subheader("📈 Closing Price Comparison")
        fig_close = go.Figure()
        for company, data in combined_data.items():
            fig_close.add_trace(go.Scatter(x=data.index, y=data["Close"], mode='lines', name=company))
        fig_close.update_layout(title="Closing Prices", xaxis_title="Date", yaxis_title="Price")
        st.plotly_chart(fig_close, use_container_width=True)

        st.subheader("📉 Daily Return Comparison")
        fig_return = go.Figure()
        for company, data in combined_data.items():
            fig_return.add_trace(go.Scatter(x=data.index, y=data["Daily Return"], mode='lines', name=company))
        fig_return.update_layout(title="Daily Returns", xaxis_title="Date", yaxis_title="Return")
        st.plotly_chart(fig_return, use_container_width=True)

        # --- Candlestick Chart ---
        st.subheader("📉 Candlestick Chart (Sample: TCS)")
        tcs_data = combined_data.get('TCS', None)
        if tcs_data is not None:
            fig_candle = go.Figure(data=[go.Candlestick(x=tcs_data.index,
                                                     open=tcs_data['Open'],
                                                     high=tcs_data['High'],
                                                     low=tcs_data['Low'],
                                                     close=tcs_data['Close'])])
            fig_candle.update_layout(title="Candlestick Chart for TCS", xaxis_title="Date", yaxis_title="Price")
            st.plotly_chart(fig_candle)

        # --- Volatility Chart ---
        st.subheader("📊 30-Day Rolling Volatility Comparison")
        fig_volatility = go.Figure()
        for company, data in combined_data.items():
            fig_volatility.add_trace(go.Scatter(x=data.index, y=data["Volatility"], mode='lines', name=company))
        fig_volatility.update_layout(title="30-Day Volatility", xaxis_title="Date", yaxis_title="Volatility")
        st.plotly_chart(fig_volatility, use_container_width=True)

        st.subheader("📋 Key Stats (Latest)")
        stats_df = pd.DataFrame(key_stats_rows)
        st.dataframe(stats_df, use_container_width=True)

        for company, data in combined_data.items():
            st.download_button(f"📥 Download {company} Data", data.to_csv().encode('utf-8'), f"{company}_stock_data.csv", "text/csv")
    else:
        st.info("Please select at least one company with available data.")

    # Alert for Price Crossing Threshold
    for company, data in combined_data.items():
        if data['Close'].iloc[-1] > price_alerts.get(company, 0):
            st.markdown(f"🚨 **Price Alert**: {company} has crossed your set threshold with a price of {data['Close'].iloc[-1]}")

# ========== EXCHANGE RATES TAB (Real-Time Alerts) ==========
with tab2:
    st.sidebar.header("💱 Forex Filters")
    selected_pairs = st.sidebar.multiselect("Select Currency Pairs", list(forex_pairs.keys()), default=["USD/INR", "EUR/INR"])
    
    exchange_alerts = {}

    for pair in selected_pairs:
        base, target = forex_pairs[pair]
        exchange_alerts[pair] = exchange_alerts.get(pair, 0) or st.sidebar.number_input(f"Set alert for {pair} (Rate)", min_value=0.0)

    st.subheader("💱 Exchange Rates Overview (Real-time & Last 7 Days)")
    today = datetime.today()
    all_data = []

    for pair in selected_pairs:
        base, target = forex_pairs[pair]
        st.markdown(f"### {pair}")

        rate_rows = []
        for i in range(7):
            date = today - timedelta(days=i)
            try:
                # Use current rate for all days (as historical API needs paid tier)
                rate = get_exchange_rate(base, target)
                if rate:
                    rate_rows.append({"Date": date.strftime("%Y-%m-%d"), "Rate": round(rate, 4)})
                    # Check if rate crosses alert threshold
                    if rate > exchange_alerts.get(pair, 0):
                        st.markdown(f"🚨 **Rate Alert**: {pair} has crossed your set threshold with a rate of {rate}")
            except Exception as e:
                st.error(f"Error fetching rate for {pair} on {date.strftime('%Y-%m-%d')}: {e}")

        if rate_rows:
            rate_df = pd.DataFrame(rate_rows).sort_values("Date")
            st.line_chart(rate_df.set_index("Date"))
            st.dataframe(rate_df)

            st.download_button(f"📥 Download {pair} Rates", rate_df.to_csv(index=False).encode('utf-8'), f"{pair.replace('/', '_')}_rates.csv", "text/csv")
        else:
            st.warning(f"No data found for {pair}.")
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