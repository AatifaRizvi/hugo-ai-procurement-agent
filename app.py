import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import plotly.express as px
from hugo_agent import HugoAgent

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Hugo – AI Procurement Agent",
    page_icon="🛵",
    layout="wide"
)

# =====================================================
# LOAD HUGO AGENT
# =====================================================
@st.cache_resource
def load_hugo():
    return HugoAgent()

hugo = load_hugo()

# =====================================================
# TABS
# =====================================================
tabs = st.tabs([
    "🏠 Dashboard",
    "💬 Ask Hugo",
    "📊 Analytics",
    "⚠️ Alerts",
    "🔮 Scenario Simulation"
])

# =====================================================
# 🏠 DASHBOARD
# =====================================================
with tabs[0]:
    st.title("Hugo – AI Procurement Dashboard")

    context = hugo.compute_context()

    capacity_df = pd.DataFrame(context["capacity_report"])
    bottlenecks_df = pd.DataFrame(context["bottlenecks"])
    supplier_df = pd.DataFrame(context["supplier_report"])
    alerts = context["alerts"]

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Scooter Models", len(capacity_df.columns))
    c2.metric("Bottlenecks", len(bottlenecks_df))
    c3.metric("Active Alerts", len(alerts))

    # Capacity Chart
    st.subheader("📊 Build Capacity by Model")
    cap_long = capacity_df.reset_index().melt(
        var_name="Model",
        value_name="Max Units"
    )

    fig = px.bar(
        cap_long,
        x="Model",
        y="Max Units",
        text="Max Units"
    )
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # Tables
    st.subheader("⚠️ Bottlenecks")
    st.dataframe(bottlenecks_df, use_container_width=True)

    st.subheader("🏭 Supplier Risk")
    st.dataframe(supplier_df, use_container_width=True)

# =====================================================
# 💬 ASK HUGO (CHAT MODE)
# =====================================================
with tabs[1]:
    st.header("💬 Ask Hugo – AI Reasoning Agent")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    # Show chat history
    for msg in st.session_state.chat:
        st.chat_message(msg["role"]).markdown(msg["content"])

    # Chat input
    user_input = st.chat_input(
        "Ask about capacity, bottlenecks, suppliers, demand scenarios..."
    )

    if user_input:
        st.chat_message("user").markdown(user_input)

        with st.spinner("Hugo is thinking..."):
            response = hugo.ask(user_input)

        st.chat_message("assistant").markdown(response)

        st.session_state.chat.append({
            "role": "user",
            "content": user_input
        })
        st.session_state.chat.append({
            "role": "assistant",
            "content": response
        })

# =====================================================
# 📊 ANALYTICS
# =====================================================
with tabs[2]:
    st.header("📊 System-Wide Analysis")
    st.info("High-level AI-generated overview of operations.")
    st.markdown(hugo.run_full_analysis())

# =====================================================
# ⚠️ ALERTS
# =====================================================
with tabs[3]:
    st.header("⚠️ Automation Alerts")

    if alerts:
        for alert in alerts:
            st.warning(alert)
    else:
        st.success("No critical alerts detected.")

# =====================================================
# 🔮 SCENARIO SIMULATION
# =====================================================
with tabs[4]:
    st.header("🔮 Demand Spike Simulation")

    spike = st.slider(
        "Increase demand by (%)",
        min_value=0,
        max_value=100,
        value=20
    )

    if st.button("Run Simulation"):
        # --- Ensure all capacity columns are numeric ---
        numeric_capacity_df = capacity_df.apply(pd.to_numeric, errors='coerce')

        # --- Run the demand spike simulation ---
        simulated = numeric_capacity_df * (1 + spike / 100)
        simulated = simulated.astype(int)  # optional: convert to integers

        # Prepare for chart
        sim_long = simulated.reset_index().melt(
            var_name="Model",
            value_name="Simulated Units"
        )

        fig2 = px.bar(
            sim_long,
            x="Model",
            y="Simulated Units",
            text="Simulated Units"
        )
        fig2.update_layout(template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("⚠️ Likely Bottlenecks")
        st.dataframe(bottlenecks_df, use_container_width=True)

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("Hugo AI Procurement Agent • Hackathon Demo Ready 🚀")
