
import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
import streamlit.components.v1 as components

# --- Load Local Storage ---
components.html("""
<script>
  const keys = [
    "msty_theme", "msty_total_shares", "msty_avg_div",
    "msty_exit_price", "msty_hedge_shares", "msty_holding_months",
    "msty_reinvest_percent", "msty_expiry"
  ];
  keys.forEach(k => {
    let v = localStorage.getItem(k);
    if (v !== null) {
      let inputs = window.parent.document.querySelectorAll('[data-testid="stNumberInput"] input, [data-testid="stSlider"] input, [data-testid="stSelectbox"] select');
      if (inputs && inputs.length > 0) {
        inputs.forEach(el => {
          if (el && v && el.placeholder === k) {
            el.value = v;
            el.dispatchEvent(new Event('input', { bubbles: true }));
          }
        });
      }
    }
  });
</script>

<script>
  const keys = ["msty_theme", "msty_total_shares", "msty_avg_div", "msty_exit_price", "msty_hedge_shares"];
  keys.forEach(k => {
    let v = localStorage.getItem(k);
    if (v !== null) {
      let input = window.parent.document.querySelectorAll('[data-testid="stNumberInput"] input');
      if (input && input.length > 0) {
        input.forEach(el => {
          if (el && v && !isNaN(v) && el.placeholder === k) {
            el.value = v;
            el.dispatchEvent(new Event('input', { bubbles: true }));
          }
        });
      }
    }
  });
</script>
""", height=0)

# --- Setup UI Theme ---
if "theme" not in st.session_state:
    st.session_state["theme"] = "Light"
theme = st.radio("Theme", ["Light", "Dark"], index=0 if st.session_state["theme"] == "Light" else 1, horizontal=True)
if st.button("Save Theme Preference"):
    st.session_state["saved_theme"] = theme
    components.html(f"""
    <script>
      localStorage.setItem("msty_theme", "{theme}");
    </script>
    """, height=0)
    st.success(f"Saved {theme} mode for this browser.")

if theme == "Dark":
    st.markdown("""
        <style>
        html, body, [class*="css"]  {
            background-color: #1e1e1e;
            color: #f1f1f1;
        }
        </style>
    """, unsafe_allow_html=True)

st.title("📊 MSTY Stock Monitoring & Simulation Suite")

tabs = st.tabs(["📊 Compounding Simulator", "📈 Market Monitoring", "📐 Cost Basis Tools", "🛡️ Hedging Tools", "📤 Export Center"])

# --- Compounding Simulator ---
with tabs[0]:
    st.header("📊 MSTY Compounding Simulator")
    total_shares = st.number_input("Total Share Count", min_value=0, value=10000, key="sim_total_shares")
    avg_div = st.number_input("Average Monthly Dividend per Share ($)", min_value=0.0, value=2.0, key="sim_avg_div")

    # Save inputs to localStorage
    components.html(f"""
    <script>
      localStorage.setItem("msty_total_shares", "{total_shares}");
      localStorage.setItem("msty_avg_div", "{avg_div}");
    </script>
    """, height=0)

# --- Hedging Tools ---
with tabs[1]:
    st.header("🛡️ Hedge Estimator")
    shares_to_hedge = st.number_input("Shares to Hedge", value=10000, key="hedge_shares")
    exit_price = st.number_input("Expected Exit Price ($)", value=10.0, key="exit_price_tab1")

    # Save inputs to localStorage
    components.html(f"""
    <script>
      localStorage.setItem("msty_hedge_shares", "{shares_to_hedge}");
      localStorage.setItem("msty_exit_price", "{exit_price}");
    </script>
    """, height=0)


# Placeholder: Market Monitoring
with tabs[1]:
    st.header("📈 MSTR & Covered Call Market Monitoring (Coming Soon)")
    st.info("Live options, covered call, and IV tracking will be shown here.")

# Placeholder: Cost Basis Tools
with tabs[2]:
    st.header("📐 Cost Basis Calculator (Coming Soon)")
    st.info("Track multiple buy blocks and calculate average cost basis.")

# Placeholder: Export Center
with tabs[4]:
    st.header("📤 Export Center (Coming Soon)")
    st.info("Export simulation, hedge, and tax reports as CSV or PDF.")

# 4. Hedging Tools
with tabs[3]:
    st.header("🛡️ Hedge Estimator with Multi-Expiration Comparison")
    st.markdown("Estimate and compare the cost and outcome of put options to hedge MSTY using live data.")

    current_price = st.number_input("Current MSTR Price ($)", value=25.0, min_value=0.01)
    exercise_price = st.number_input("Expected Exit Price ($)", value=10.0, min_value=0.01, key="exit_price_tab2")
    shares_to_hedge = st.number_input("Shares to Hedge", value=10000, min_value=1, key="hedge_shares")
    max_cost_pct = st.slider("Max Hedge Cost (% of Position)", 0, 100, 5)
    contract_size = 100
    contracts = shares_to_hedge // contract_size
    position_value = current_price * shares_to_hedge
    max_cost_allowed = position_value * max_cost_pct / 100

    mstr = yf.Ticker("MSTR")
    expirations = mstr.options[:5]
    best_value = None
    summary_rows = []

    for expiry in expirations:
        try:
            chain = mstr.option_chain(expiry)
            puts = chain.puts.copy()
            puts["mid"] = (puts["bid"] + puts["ask"]) / 2
            puts = puts[puts["strike"] >= exercise_price]
            puts["cost"] = puts["mid"] * contracts
            puts["cash_out"] = contracts * contract_size * (puts["strike"] - exercise_price)
            puts["value_score"] = puts["cash_out"] / puts["cost"]

            top = puts.sort_values("value_score", ascending=False).head(1).copy()
            if not top.empty:
                top["expiry"] = expiry
                summary_rows.append(top)
                if best_value is None or top.iloc[0]["value_score"] > best_value["value_score"]:
                    best_value = top.iloc[0]
        except Exception:
            continue

    if summary_rows:
        summary_df = pd.concat(summary_rows)
        summary_df = summary_df[["expiry", "strike", "mid", "cost", "cash_out", "value_score"]]
        summary_df.columns = ["Expiry", "Strike", "Premium", "Total Cost", "Cash Out", "Value Score"]

        st.dataframe(summary_df.style.format({
            "Premium": "${:,.2f}",
            "Total Cost": "${:,.2f}",
            "Cash Out": "${:,.2f}",
            "Value Score": "{:.2f}"
        }))

        fig = px.bar(summary_df, x="Strike", y="Value Score", color="Expiry", barmode="group",
                     title="Hedge Value Score by Strike and Expiry")
        st.plotly_chart(fig, use_container_width=True)

        st.download_button("Download Hedge Comparison CSV", summary_df.to_csv(index=False), "hedge_comparison.csv")

        if best_value is not None:
            st.success(f"Best Hedge: {best_value['expiry']} @ ${best_value['strike']} strike")
            st.info(f"Estimated Cost: ${best_value['cost']:,.2f} — Max Allowed: ${max_cost_allowed:,.2f}")
            if best_value['cost'] > max_cost_allowed:
                st.warning("⚠️ This hedge exceeds your maximum allowed cost threshold!")
    else:
        st.warning("No suitable hedge options found above your exit price.")


# 3. Cost Basis Tools
with tabs[2]:
    st.header("📐 Cost Basis Calculator")
    st.markdown("Enter your share blocks below:")

    cb_data = st.data_editor(
        pd.DataFrame({"Shares": [0], "Price Per Share": [0.00]}),
        num_rows="dynamic",
        use_container_width=True
    )

    if not cb_data.empty and cb_data["Shares"].sum() > 0:
        total_shares = cb_data["Shares"].sum()
        total_cost = (cb_data["Shares"] * cb_data["Price Per Share"]).sum()
        weighted_avg = total_cost / total_shares
        st.success(f"Weighted Avg Cost: ${weighted_avg:.2f} for {total_shares:,.0f} shares")
        st.download_button("📥 Download Cost Basis CSV", cb_data.to_csv(index=False), "cost_basis.csv")


# 5. Export Center
with tabs[4]:
    st.header("📤 Export Center")
    st.markdown("Export your results below:")

    if "df_view" in locals():
        st.download_button("📊 Download Projection CSV", df_view.to_csv(index=False), "projection.csv")

    if "summary_df" in locals():
        st.download_button("🛡️ Download Hedge CSV", summary_df.to_csv(index=False), "hedging.csv")

    if "cb_data" in locals():
        st.download_button("📐 Download Cost Basis CSV", cb_data.to_csv(index=False), "cost_basis.csv")

    st.subheader("📄 PDF Export (Coming Soon)")
    st.write("PDF generation and formatting is in progress.")

    st.subheader("📧 Send Report via Email")
    email = st.text_input("Enter your email address:")
    if st.button("Send Report via Email"):
        st.info(f"Reports will be emailed to {email} once integration is live.")

with tabs[4]:
    st.header("📤 Export Center")
    st.markdown("Export your results below:")

    # Sample access to projection table
    if "df_view" in locals():
        st.download_button("📊 Download Projection CSV", df_view.to_csv(index=False), "projection.csv")

    # Sample access to hedge summary
    if "summary_df" in locals():
        st.download_button("🛡️ Download Hedge CSV", summary_df.to_csv(index=False), "hedging.csv")

    # Cost basis export already exists in tab 3
    st.info("Projections, hedge results, and cost basis can all be exported as CSV.")

# 2. Market Monitoring
with tabs[1]:
    st.header("📈 MSTR Market Monitoring")

    ticker = yf.Ticker("MSTR")
    latest_price = ticker.history(period="1d")["Close"].iloc[-1]
    st.metric("Current MSTR Price", f"${latest_price:.2f}")

    st.subheader("Options Volume & Open Interest (Latest Expiry)")
    expiry = ticker.options[0]
    options = ticker.option_chain(expiry)
    calls = options.calls
    puts = options.puts

    total_call_oi = calls["openInterest"].sum()
    total_put_oi = puts["openInterest"].sum()
    total_call_vol = calls["volume"].sum()
    total_put_vol = puts["volume"].sum()

    st.metric("Total Call OI", f"{total_call_oi:,}")
    st.metric("Total Put OI", f"{total_put_oi:,}")
    st.metric("Total Call Volume", f"{total_call_vol:,}")
    st.metric("Total Put Volume", f"{total_put_vol:,}")

    st.subheader("📉 Implied Volatility Chart")
    calls["mid"] = (calls["bid"] + calls["ask"]) / 2
    fig_iv = px.line(calls, x="strike", y="impliedVolatility", title="Call Option IV vs Strike")
    st.plotly_chart(fig_iv, use_container_width=True)
