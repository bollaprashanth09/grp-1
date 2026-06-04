# app.py

import streamlit as st
import pandas as pd
import numpy as np
import requests
import yfinance as yf
import plotly.graph_objects as go
from ta.momentum import RSIIndicator

st.set_page_config(
    page_title="AI Financial Advisor",
    layout="wide"
)

st.title("💰 AI Financial Advisor Platform")

# --------------------------------
# Sidebar
# --------------------------------

st.sidebar.header("Financial Profile")

income = st.sidebar.number_input(
    "Monthly Income",
    0,
    10000000,
    50000
)

expenses = st.sidebar.number_input(
    "Monthly Expenses",
    0,
    10000000,
    25000
)

goal = st.sidebar.number_input(
    "Savings Goal",
    0,
    100000000,
    1000000
)

risk = st.sidebar.selectbox(
    "Risk Appetite",
    ["Low","Medium","High"]
)

# --------------------------------
# NSE DATA
# --------------------------------

@st.cache_data(ttl=300)
def get_nse_stocks():

    session = requests.Session()

    headers = {
        "User-Agent":"Mozilla/5.0",
        "Referer":"https://www.nseindia.com/"
    }

    session.get(
        "https://www.nseindia.com",
        headers=headers
    )

    url = "https://www.nseindia.com/api/market-data-pre-open?key=ALL"

    data = session.get(
        url,
        headers=headers
    ).json()

    rows = []

    for item in data["data"]:

        try:

            m = item["metadata"]

            rows.append({
                "Symbol":m["symbol"],
                "Company":m["companyName"],
                "Price":m["lastPrice"],
                "Change %":m["pChange"]
            })

        except:
            pass

    return pd.DataFrame(rows)

# --------------------------------
# Tabs
# --------------------------------

tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
    "Dashboard",
    "NSE Market",
    "Stock Screener",
    "SIP Planner",
    "Bitcoin",
    "Advisor"
])

# --------------------------------
# DASHBOARD
# --------------------------------

with tab1:

    savings = income - expenses

    st.metric("Income",f"₹{income:,.0f}")
    st.metric("Expenses",f"₹{expenses:,.0f}")
    st.metric("Savings",f"₹{savings:,.0f}")

    if income > 0:

        rate = (savings/income)*100

        st.success(
            f"Savings Rate : {rate:.2f}%"
        )

# --------------------------------
# NSE MARKET
# --------------------------------

with tab2:

    st.subheader("📈 Live NSE Market")

    try:

        market = get_nse_stocks()

        st.dataframe(
            market,
            use_container_width=True
        )

        stock = st.selectbox(
            "Select Stock",
            market["Symbol"]
        )

        ticker = stock + ".NS"

        data = yf.download(
            ticker,
            period="1y",
            progress=False
        )

        st.metric(
            "Current Price",
            f"₹{data['Close'].iloc[-1]:.2f}"
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["Close"]
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    except Exception as e:

        st.error(e)

# --------------------------------
# AI STOCK SCREENER
# --------------------------------

with tab3:

    st.subheader("🚀 AI Stock Recommendations")

    if st.button("Scan Market"):

        market = get_nse_stocks()

        recommendations = []

        for sym in market["Symbol"][:100]:

            try:

                ticker = sym + ".NS"

                df = yf.download(
                    ticker,
                    period="6mo",
                    progress=False
                )

                if len(df) < 60:
                    continue

                df["MA20"] = df["Close"].rolling(20).mean()
                df["MA50"] = df["Close"].rolling(50).mean()

                rsi = RSIIndicator(
                    df["Close"]
                ).rsi()

                latest_rsi = rsi.iloc[-1]

                latest = df.iloc[-1]

                signal = "HOLD"

                if (
                    latest["MA20"] >
                    latest["MA50"]
                    and latest_rsi < 70
                ):
                    signal = "BUY"

                elif latest_rsi > 70:
                    signal = "SELL"

                recommendations.append([
                    sym,
                    round(float(latest_rsi),2),
                    signal
                ])

            except:
                pass

        rec_df = pd.DataFrame(
            recommendations,
            columns=[
                "Stock",
                "RSI",
                "Signal"
            ]
        )

        st.dataframe(
            rec_df[
                rec_df["Signal"]=="BUY"
            ]
        )

# --------------------------------
# SIP
# --------------------------------

with tab4:

    st.subheader("💵 SIP Calculator")

    sip = st.number_input(
        "Monthly SIP",
        500,
        100000,
        5000
    )

    years = st.slider(
        "Years",
        1,
        30,
        10
    )

    expected_return = st.slider(
        "Expected Return %",
        5,
        20,
        12
    )

    n = years*12

    fv = sip * (
        (
            ((1+expected_return/100/12)**n)-1
        )/(expected_return/100/12)
    )*(1+expected_return/100/12)

    st.success(
        f"Future Value : ₹{fv:,.0f}"
    )

    st.subheader("ETF Recommendations")

    etfs = pd.DataFrame({
        "ETF":[
            "NIFTYBEES",
            "BANKBEES",
            "ITBEES",
            "GOLDBEES"
        ],
        "Type":[
            "Index",
            "Banking",
            "IT",
            "Gold"
        ]
    })

    st.dataframe(etfs)

# --------------------------------
# BITCOIN
# --------------------------------

with tab5:

    st.subheader("₿ Bitcoin")

    btc = yf.download(
        "BTC-USD",
        period="1y",
        progress=False
    )

    st.metric(
        "Bitcoin Price",
        f"${btc['Close'].iloc[-1]:,.0f}"
    )

    fig2 = go.Figure()

    fig2.add_trace(
        go.Scatter(
            x=btc.index,
            y=btc["Close"]
        )
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# --------------------------------
# ADVISOR
# --------------------------------

with tab6:

    st.subheader("🤖 Financial Advisor")

    savings = income - expenses

    if savings <= 0:

        st.error(
            "Reduce expenses and create emergency fund."
        )

    elif savings < 10000:

        st.warning("""
        Recommended:
        • FD
        • Liquid Fund
        • Emergency Fund
        """)

    elif savings < 30000:

        st.info("""
        Recommended:
        • 50% SIP
        • 30% ETF
        • 20% Gold ETF
        """)

    else:

        st.success("""
        Recommended:
        • 40% Stocks
        • 30% Mutual Funds
        • 20% ETFs
        • 10% Bitcoin
        """)

    st.subheader("Goal Planning")

    if savings > 0:

        months = goal / savings

        st.write(
            f"Goal can be achieved in {months:.1f} months"
        )

    st.subheader("Risk Based Allocation")

    if risk == "Low":

        st.write({
            "Debt":50,
            "ETF":20,
            "Gold":20,
            "Cash":10
        })

    elif risk == "Medium":

        st.write({
            "Stocks":30,
            "MF":40,
            "ETF":20,
            "Gold":10
        })

    else:

        st.write({
            "Stocks":50,
            "ETF":20,
            "MF":20,
            "Bitcoin":10
        })