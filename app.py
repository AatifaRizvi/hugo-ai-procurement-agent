# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from hugo_agent import HugoAgent

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="Hugo – AI Procurement Agent",
    page_icon="🛵",
    layout="wide"
)

# ---------------------------
# Initialize Hugo Agent
# ---------------------------
@st.cache_resource
def load_hugo_agent():
    return HugoAgent()

hugo = load_hugo_agent()

# ---------------------------
# Tabs
# ---------------------------
tabs = st.tabs(["🏠 Dashboard", "💬 Ask Hugo", "📊 Analytics", "⚠️ Alerts", "🔮 Scenario Simulation"])

# ---------------------------
# Dashboard Tab
# ---------------------------
with tabs[0]:
    st.title("Hugo – AI Procurement Dashboard")
    
    context = hugo.compute_context()
    capacity_report = pd.DataFrame(context["capacity_report"])
    bottlenecks = pd.DataFrame(context["bottlenecks"])
    supplier_report = pd.DataFrame(context["supplier_report"])
    alerts = context["alerts"]

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Scooter Models", len(capacity_report.columns))
    col2.metric("Bottlenecked Parts", bottlenecks.shape[0])
    col3.metric("Supplier Alerts", len(alerts))

    # Convert capacity to long format for Plotly
    capacity_long = capacity_report.reset_index().melt(
        var_name='model',
        value_name='max_units'
    )

    # Capacity Chart
    st.subheader("📊 Build Capacity by Model")
    fig = px.bar(
        capacity_long,
        x='model',
        y='max_units',
        color='max_units',
        labels={'model': 'Scooter Model', 'max_units': 'Max Units'},
        text='max_units'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Bottleneck Table
    st.subheader("⚠️ Bottleneck Analysis")
    st.dataframe(bottlenecks)

    # Supplier Risk Table
    st.subheader("📈 Supplier Risk")
    st.dataframe(supplier_report)

# ---------------------------
# LLM Query Tab
# ---------------------------
with tabs[1]:
    st.header("💬 Ask Hugo Any Operational Question")
    question = st.text_input(
        "Enter your question:",
        placeholder="e.g., Which parts are at risk if webshop demand spikes 20%?"
    )
    if st.button("Ask Hugo"):
        with st.spinner("Hugo is reasoning..."):
            response = hugo.ask(question)
        st.markdown("### Hugo's Answer")
        st.markdown(response)

# ---------------------------
# Analytics Tab
# ---------------------------
with tabs[2]:
    st.header("📊 Detailed Analytics")
    st.subheader("Build Capacity Table")
    st.dataframe(capacity_report)
    
    st.subheader("Bottleneck Heatmap")
    if not bottlenecks.empty:
        corr = bottlenecks.select_dtypes(include='number').corr()
        fig2 = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r')
        st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# Alerts Tab
# ---------------------------
with tabs[3]:
    st.header("⚠️ Automation Alerts")
    if alerts:
        for a in alerts:
            st.warning(a)
    else:
        st.success("No critical alerts currently.")

# ---------------------------
# Scenario Simulation Tab
# ---------------------------
with tabs[4]:
    st.header("🔮 What-If Scenario Simulation")
    spike = st.slider("Increase webshop demand by (%)", 0, 100, 20)
    if st.button("Run Simulation"):
        with st.spinner("Running scenario simulation..."):
            # Copy the original capacity_report and adjust for spike
            simulated_capacity = capacity_report.copy()
            simulated_capacity = simulated_capacity.apply(lambda x: (x * (1 + spike/100)).astype(int))
            
            # Convert to long format
            sim_long = simulated_capacity.reset_index().melt(
                var_name='model',
                value_name='max_units'
            )
            
            # Plot simulated capacity
            fig3 = px.bar(
                sim_long,
                x='model',
                y='max_units',
                color='max_units',
                labels={'model':'Scooter Model', 'max_units':'Simulated Units'},
                text='max_units'
            )
            st.plotly_chart(fig3, use_container_width=True)
            
            # Show bottlenecks (use original for now, can extend with prediction)
            st.subheader("Predicted Bottlenecks / At-Risk Parts")
            st.dataframe(bottlenecks)

# ---------------------------
# Footer / Example Questions
# ---------------------------
st.markdown("---")
st.subheader("💡 Example Questions")
st.markdown("""
- How many scooters can we build next week?
- Which suppliers are risky this month?
- What parts are causing production delays?
- If demand increases by 20%, what breaks first?
- Which supplier should we renegotiate with?
""")
