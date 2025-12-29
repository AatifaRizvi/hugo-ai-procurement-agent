import streamlit as st
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
# Sidebar
# ---------------------------
st.sidebar.title("🧠 Hugo Controls")
mode = st.sidebar.selectbox(
    "Select Mode",
    ["Ask Anything (LLM)", "Build Capacity", "Supplier Risk", "Bottleneck Analysis"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Model:** gemma3:4b (Ollama)")
st.sidebar.markdown("**UI:** Streamlit")

# ---------------------------
# Main UI
# ---------------------------
st.title("🛵 Hugo – Procurement AI Agent for Voltway")
st.markdown("Ask operational questions, detect risks, and get AI-powered recommendations.")

question = st.text_input(
    "💬 Ask Hugo a question",
    placeholder="e.g. How many S2 V2 scooters can we build next week?"
)

run_btn = st.button("🚀 Run Analysis")

# ---------------------------
# Run Logic
# ---------------------------
if run_btn and question:

    with st.spinner("Hugo is thinking..."):

        if mode == "Build Capacity":
            response = hugo.capacity_engine.compute_capacity()

        elif mode == "Supplier Risk":
            response = hugo.supplier_engine.analyze_suppliers()

        elif mode == "Bottleneck Analysis":
            response = hugo.bottleneck_engine.analyze_bottlenecks()

        else:  # Ask Anything LLM
            response = hugo.ask(question)

    st.success("Analysis Complete")

    st.subheader("📊 Hugo's Output")

    if isinstance(response, dict) or isinstance(response, list):
        st.json(response)
    else:
        st.markdown(response)

# ---------------------------
# Example Questions
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
