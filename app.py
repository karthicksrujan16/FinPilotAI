import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="FinPilot AI",
    page_icon="📈",
    layout="wide"
)

st.title("📈 FinPilot AI")
st.subheader("AI Powered Stock Analysis Dashboard")

# ----------------------------
# STOCK INPUT
# ----------------------------
# ----------------------------
# STOCK INPUT
# ----------------------------

market = st.selectbox(
    "Select Exchange",
    ["US", "NSE", "BSE"]
)

if market == "US":
    default = "AAPL"
elif market == "NSE":
    default = "RELIANCE"
else:
    default = "500325"   # Reliance BSE code

stock_input = st.text_input(
    "Enter Stock Symbol",
    default
).upper()

# Convert to Yahoo Finance ticker
if market == "NSE":
    ticker = stock_input + ".NS"
elif market == "BSE":
    ticker = stock_input + ".BO"
else:
    ticker = stock_input

if ticker:

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Currency Symbol
        currency = info.get("currency", "USD")

        symbols = {
            "USD": "$",
            "INR": "₹",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥"
        }

        symbol = symbols.get(currency, currency)

        current_price = info.get("currentPrice", "N/A")
        market_cap = info.get("marketCap", None)
        pe_ratio = info.get("trailingPE", "N/A")
        company = info.get("longName", ticker)

        st.success(f"Showing Analysis for {company}")

        # ----------------------------
        # METRICS
        # ----------------------------

        col1, col2, col3 = st.columns(3)

        with col1:
            if current_price != "N/A":
                st.metric("Current Price", f"{symbol}{current_price}")
            else:
                st.metric("Current Price", "N/A")

        with col2:
            if market_cap:

                if currency == "INR":
                    market_cap_display = f"₹{market_cap/1e12:.2f} Lakh Cr"
                else:
                    market_cap_display = f"{symbol}{market_cap/1e9:.2f} B"

                st.metric("Market Cap", market_cap_display)

            else:
                st.metric("Market Cap", "N/A")

        with col3:
            st.metric("P/E Ratio", pe_ratio)

        st.divider()

        # ----------------------------
        # COMPANY DESCRIPTION
        # ----------------------------

        st.subheader("🏢 Company Overview")

        st.write(
            info.get(
                "longBusinessSummary",
                "No description available."
            )
        )

        st.divider()

        # ----------------------------
        # PRICE HISTORY
        # ----------------------------

        hist = stock.history(period="6mo")

        hist["MA50"] = hist["Close"].rolling(50).mean()
        hist["MA200"] = hist["Close"].rolling(200).mean()

        st.subheader("📈 Stock Price Chart")

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=hist.index,
                y=hist["Close"],
                mode="lines",
                name="Close Price"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=hist.index,
                y=hist["MA50"],
                mode="lines",
                name="50 Day MA"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=hist.index,
                y=hist["MA200"],
                mode="lines",
                name="200 Day MA"
            )
        )

        fig.update_layout(
            template="plotly_dark",
            title=f"{company} Price Trend",
            xaxis_title="Date",
            yaxis_title=f"Price ({currency})",
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # ----------------------------
        # AI RECOMMENDATION
        # ----------------------------

        st.subheader("🤖 FinPilot AI Recommendation")

        latest = hist["Close"].iloc[-1]
        ma50 = hist["MA50"].iloc[-1]

        if pd.notna(ma50):

            if latest > ma50:
                st.success("🟢 BUY")

                st.write("""
The stock is trading above its 50-Day Moving Average.

This generally indicates positive momentum and a bullish trend.

Suitable for investors looking for growth opportunities.
""")

            elif latest < ma50:

                st.error("🔴 SELL")

                st.write("""
The stock is trading below its 50-Day Moving Average.

This indicates weakness in the current trend.

Existing investors should review risk before holding.
""")

            else:

                st.warning("🟡 HOLD")

        else:
            st.info("Not enough historical data.")

        st.divider()

        # ----------------------------
        # EXTRA INFORMATION
        # ----------------------------

        st.subheader("📋 Additional Details")

        c1, c2 = st.columns(2)

        with c1:
            st.write("**Sector:**", info.get("sector", "N/A"))
            st.write("**Industry:**", info.get("industry", "N/A"))
            st.write("**Country:**", info.get("country", "N/A"))
            st.write("**Website:**", info.get("website", "N/A"))

        with c2:
            st.write("**52 Week High:**", info.get("fiftyTwoWeekHigh", "N/A"))
            st.write("**52 Week Low:**", info.get("fiftyTwoWeekLow", "N/A"))
            st.write("**Dividend Yield:**", info.get("dividendYield", "N/A"))
            st.write("**Beta:**", info.get("beta", "N/A"))

    except Exception as e:
        st.error("Unable to fetch stock data.")
        st.write(e)