
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MSTY Stock Tools", layout="wide")

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
    total_shares = st.number_input("Total Share Count", min_value=0, value=10000, key="shares_tab1")
    avg_cost = st.number_input("Weighted Average Cost Basis ($)", min_value=0.0, value=25.00, key="cost_tab1")
    holding_months = st.slider("Holding Period (Months)", min_value=1, max_value=120, value=24, key="months_tab1")
    avg_div = st.number_input("Average Monthly Dividend per Share ($)", min_value=0.0, value=2.0, key="div_tab1")

    fed_tax = st.slider("Federal Tax Rate (%)", 0, 50, 20, key="fedtax_tab1")
    state_tax = st.slider("State Tax Rate (%)", 0, 20, 5, key="statetax_tab1")
    dependents = st.number_input("Number of Dependents", min_value=0, value=0, key="deps_tab1")
    acct_type = st.selectbox("Account Type", ["Taxable", "Tax Deferred"], key="acct_tab1")

    drip = st.checkbox("Reinvest Dividends?", key="drip_tab1")
    if drip:
        reinvest_percent = st.slider("Percent of Dividends to Reinvest (%)", 0, 100, 100, key="reinv_pct_tab1")
    else:
        reinvest_percent = 0
        withdrawal = st.number_input("Withdraw this Dollar Amount Monthly ($)", min_value=0, value=2000, key="withd_tab1")

    reinvest_price = st.number_input("Average Reinvestment Share Price ($)", min_value=1.0, value=25.0, key="reinv_price_tab1")
    frequency = st.selectbox("How would you like to view the projection?", ["Monthly", "Yearly", "Total"], key="freq_tab1")
    run_sim = st.button("Run Simulation", key="sim_btn_tab1")

    if run_sim:
        monthly_data = []
        shares = total_shares
        total_dividends = 0
        total_reinvested = 0

        for month in range(1, holding_months + 1):
            gross_div = shares * avg_div
            tax = 0 if acct_type == "Tax Deferred" else gross_div * (fed_tax + state_tax) / 100
            net_div = gross_div - tax
            if drip:
                reinvest_amount = net_div * (reinvest_percent / 100)
            else:
                reinvest_amount = max(0, net_div - withdrawal)
            new_shares = reinvest_amount / reinvest_price
            shares += new_shares
            total_dividends += net_div
            total_reinvested += reinvest_amount
            monthly_data.append({
                "Month": month,
                "Year": (month - 1) // 12 + 1,
                "Shares": shares,
                "Net Dividends": net_div,
                "Reinvested": reinvest_amount
            })

        df = pd.DataFrame(monthly_data)
        if frequency == "Monthly":
            df_view = df.copy()
            df_view["Period"] = df_view["Month"]
        elif frequency == "Yearly":
            df_view = df.groupby("Year").agg({
                "Shares": "last",
                "Net Dividends": "sum",
                "Reinvested": "sum"
            }).reset_index().rename(columns={"Year": "Period"})
        else:
            df_view = pd.DataFrame([{
                "Period": "Total",
                "Shares": df["Shares"].iloc[-1],
                "Net Dividends": df["Net Dividends"].sum(),
                "Reinvested": df["Reinvested"].sum()
            }])

        st.success(f"📈 Final Share Count: {shares:,.2f}")
        st.success(f"💸 Total Dividends Collected: ${total_dividends:,.2f}")
        st.success(f"🔁 Total Reinvested: ${total_reinvested:,.2f}")
        fig = px.bar(df_view, x="Period", y="Shares", title=f"Share Count View: {frequency}")
        st.plotly_chart(fig)
        st.subheader("📋 Projection Table")
        st.dataframe(df_view.style.format({
            "Shares": "{:,.2f}",
            "Net Dividends": "${:,.2f}",
            "Reinvested": "${:,.2f}"
        }))

# Tabs 2-5 placeholder
for i, title in enumerate(["📈 Market Monitoring", "📐 Cost Basis Tools", "🛡️ Hedging Tools", "📤 Export Center"], start=1):
    with tabs[i]:
        st.header(f"{title} (Coming Soon)")
        st.info("This section will be developed next.")
