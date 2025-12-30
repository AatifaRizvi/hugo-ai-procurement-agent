import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from hugo_agent import HugoAgent

# =====================================================
# UTILS
# =====================================================
def make_df_arrow_safe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensures dataframe is Arrow-compatible by converting
    object-type columns to strings.
    """
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str)
    return df


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

    # ---------------- Metrics ----------------
    c1, c2, c3 = st.columns(3)
    c1.metric("Scooter Models", len(capacity_df.columns))
    c2.metric("Bottlenecks", len(bottlenecks_df))
    c3.metric("Active Alerts", len(alerts))

    # ---------------- Capacity Chart ----------------
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
    st.plotly_chart(fig, width="stretch",key="dashboard_capacity_chart")

    # ---------------- Tables ----------------
    st.subheader("⚠️ Bottlenecks")
    st.dataframe(
        make_df_arrow_safe(bottlenecks_df),
        width="stretch"
    )

    st.subheader("🏭 Supplier Risk")
    st.dataframe(
        make_df_arrow_safe(supplier_df),
        width="stretch"
    )

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
    st.header("🔮 Demand Spike Simulation (Risk-Based)")

    spike = st.slider(
        "Increase demand by (%)",
        min_value=0,
        max_value=100,
        value=20
    )

    if st.button("Run Simulation"):
        with st.spinner("Recomputing operational risk under demand spike..."):
            sim_capacity, sim_bottlenecks, sim_snapshot = hugo.simulate_demand_spike(spike)

        # -------------------------------
        # Capacity (unchanged by design)
        # -------------------------------
        st.subheader("📊 Build Capacity (Immediate)")

        st.info(
            "Capacity represents immediate build potential. "
            "Demand spikes affect risk over time, not instant capacity."
        )

        sim_capacity_df = pd.DataFrame(sim_capacity)

        cap_long = sim_capacity_df.reset_index().melt(
            var_name="Model",
            value_name="Max Units"
        )

        fig_cap = px.bar(
            cap_long,
            x="Model",
            y="Max Units",
            text="Max Units",
            title="Immediate Build Capacity"
        )
        fig_cap.update_layout(template="plotly_white")

        st.plotly_chart(
            fig_cap,
            width="stretch",
            key=f"sim_capacity_chart_{spike}"
        )

        # -------------------------------
        # Days of Cover (THIS WILL CHANGE)
        # -------------------------------
        st.subheader("🔥 Inventory Risk After Demand Spike")

        sim_parts_df = pd.DataFrame(sim_snapshot)

        doc_df = sim_parts_df[["part_id", "days_of_cover"]].copy()
        doc_df = doc_df.sort_values("days_of_cover")

        fig_doc = px.bar(
            doc_df,
            x="part_id",
            y="days_of_cover",
            title="Days of Cover After Demand Spike",
            text="days_of_cover"
        )
        fig_doc.update_layout(template="plotly_white")

        st.plotly_chart(
            fig_doc,
            width="stretch",
            key=f"days_of_cover_chart_{spike}"
        )

        st.caption(
            "Lower days of cover indicate higher stockout risk as demand increases."
        )

        # -------------------------------
        # Bottlenecks
        # -------------------------------
        st.subheader("⚠️ Bottlenecks Under Increased Demand")

        sim_bottlenecks_df = pd.DataFrame(sim_bottlenecks)

        if sim_bottlenecks_df.empty:
            st.success("No new bottlenecks detected under this demand scenario.")
        else:
            st.dataframe(
                make_df_arrow_safe(sim_bottlenecks_df),
                width="stretch"
            )

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("Hugo AI Procurement Agent • Hackathon Demo Ready")
