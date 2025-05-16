import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

st.set_page_config(page_title="MSTY Stock Monitoring & Simulation Suite", layout="wide")

st.title("📊 MSTY Stock Monitoring & Simulation Suite")

tabs = st.tabs([
    "📊 Compounding Simulator",
    "📈 Market Monitoring",
    "📐 Cost Basis Tools",
    "🛡️ Hedging Tools",
    "📤 Export Center"
])

# Tab 1: Compounding Simulator
with tabs[0]:
    st.header("📊 MSTY Compounding Simulator")
    shares = st.number_input("Total Share Count", min_value=0, value=10000)
    avg_div = st.number_input("Average Monthly Dividend per Share ($)", min_value=0.0, value=2.0)
    months = st.slider("Holding Period (Months)", 1, 120, 24)
    reinvest = st.checkbox("Reinvest Dividends?")
    price = st.number_input("Reinvestment Share Price ($)", min_value=0.1, value=25.0)
    run = st.button("Run Projection")

    if run:
        df = []
        for i in range(1, months+1):
            dividend = shares * avg_div
            new_shares = (dividend / price) if reinvest else 0
            shares += new_shares
            df.append({"Month": i, "Shares": shares, "Dividend": dividend, "Reinvested": new_shares*price})
        proj = pd.DataFrame(df)
        st.success(f"Final Share Count: {shares:,.2f}")
        st.bar_chart(proj.set_index("Month")["Shares"])
        st.dataframe(proj)

# Tab 2: Market Monitoring
with tabs[1]:
    st.header("📈 Market Monitoring: MSTR Overview")

    ticker = "MSTR"
    st.markdown(f"### 📊 Live Data for {ticker}")

    stock = yf.Ticker(ticker)
    hist = stock.history(period="1mo")

    if not hist.empty:
        st.line_chart(hist["Close"], use_container_width=True)
        st.metric("📈 Current Price", f"${hist['Close'][-1]:,.2f}")
        st.metric("📉 Day Low", f"${hist['Low'][-1]:,.2f}")
        st.metric("📈 Day High", f"${hist['High'][-1]:,.2f}")
        st.metric("📊 Volume", f"{hist['Volume'][-1]:,.0f}")
    else:
        st.error("No data found for MSTR.")

# Tab 3: Cost Basis Tools
with tabs[2]:
    st.header("📐 Cost Basis Calculator")
    st.markdown("Enter your share lots below to calculate weighted cost basis.")
    cost_data = st.data_editor(pd.DataFrame({"Shares": [0], "Price Per Share": [0.0]}),
                               num_rows="dynamic", key="cost_basis_editor")
    if not cost_data.empty:
        total_shares = cost_data["Shares"].sum()
        total_cost = (cost_data["Shares"] * cost_data["Price Per Share"]).sum()
        if total_shares > 0:
            avg_cost = total_cost / total_shares
            st.success(f"Weighted Average Cost Basis: ${avg_cost:,.2f}")
        else:
            st.warning("Enter at least one share lot.")

# Tab 4: Hedging Tools
with tabs[3]:
    st.header("🛡️ Hedge Estimator")
    hedge_shares = st.number_input("Shares to Hedge", min_value=0, value=10000)
    current_price = st.number_input("Current Share Price ($)", min_value=0.01, value=25.0)
    exit_price = st.number_input("Expected Exit Price ($)", min_value=0.01, value=10.0)
    strike_price = st.number_input("Put Option Strike Price ($)", min_value=0.01, value=25.0)
    cost_per_contract = st.number_input("Estimated Option Price per Share ($)", min_value=0.01, value=2.50)
    contracts = hedge_shares / 100
    total_cost = contracts * 100 * cost_per_contract
    payout = (strike_price - exit_price) * hedge_shares
    net = payout - total_cost
    st.metric("Total Hedge Payout", f"${payout:,.2f}")
    st.metric("Cost of Hedge", f"${total_cost:,.2f}")
    st.metric("Net Benefit", f"${net:,.2f}")

# Tab 5: Export Center
with tabs[4]:
    st.header("📤 Export Center")
    st.info("Export simulation, hedge, and cost basis results as CSV or PDF.")
    if "proj" in locals():
        st.download_button("📊 Download Projection CSV", proj.to_csv(index=False), "projection.csv")
    if "cost_data" in locals():
        st.download_button("📐 Download Cost Basis CSV", cost_data.to_csv(index=False), "cost_basis.csv", key="cost_basis_csv")