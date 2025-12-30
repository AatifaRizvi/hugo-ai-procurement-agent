This is a professionally structured, high-impact `README.md` tailored for GitHub. It highlights the technical depth of your project while making it easy for hackathon judges to understand the value proposition.

---

# 🛵 Hugo – AI Procurement Agent

**Hugo** is an AI-powered procurement and supply-chain intelligence agent. It bridges the gap between raw operational data and strategic decision-making by combining **deterministic rule-based logic** with **LLM-driven reasoning**.

Designed for hackathons and real-world operational scenarios, Hugo analyzes production capacity, detects hidden bottlenecks, assesses supplier risks from unstructured data, and simulates the impact of demand spikes.

---

## 🎯 Target Audience

* **🏆 Hackathon Judges:** For evaluating problem-solving and data utilization.
* **👨‍💻 Technical Evaluators:** For reviewing the hybrid AI architecture.
* **📊 Supply-Chain Enthusiasts:** For exploring digital twin simulations.

---

## ✨ Key Features

### 📊 Production Capacity Analysis

* Computes maximum buildable units per model based on real-time Bill of Materials (BOM) dependencies.
* Highlights specific capacity-limiting components to guide procurement priority.

### ⚠️ Bottleneck Detection

* Identifies "blocker" parts that delay production.
* Categorizes issues into inventory shortages, assembly constraints, or supplier-side delays.

### 🏭 Supplier Risk Intelligence

* **Unstructured Data Parsing:** Analyzes supplier emails (`.eml`) to extract operational signals.
* **Signal Detection:** Automatically flags delays, price hikes, and quality alerts, linking them to specific production impacts.

### 🔮 Demand Spike Simulation

* **Real-world Modeling:** Unlike simple scaling, Hugo models risk evolution. It scales consumption rates to show how quickly "Days of Cover" deplete and when new bottlenecks will emerge.

### 💬 AI Reasoning ("Ask Hugo")

* Natural-language Q&A over live operational context.
* Provides structured root-cause analysis and actionable mitigation steps using the **Mistral-7B** model.

---

## 🧠 System Architecture

Hugo utilizes a **Hybrid Intelligence** design to ensure speed, reliability, and transparency.

1. **Data Processing Layer:** (`data_processing.py`) Transforms raw data into a structured `operational_snapshot.json`.
2. **Engine Layer:** Dedicated engines for Capacity, Bottlenecks, and Supplier Risk.
3. **Reasoning Layer:** Hugging Face Inference API (Mistral-7B) for high-level insight.
4. **UI Layer:** Streamlit dashboard for interactive analytics and simulation.

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Language:** Python 3.x
* **AI/LLM:** Hugging Face Inference API (`mistralai/Mistral-7B-Instruct-v0.2`)
* **Data Science:** Pandas, NumPy
* **Visualization:** Plotly
* **Deployment:** Streamlit Cloud (Fully cloud-native)

---

## ⚙️ Installation & Usage

### Local Setup

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/hugo-ai-procurement-agent.git
cd hugo-ai-procurement-agent

```


2. **Install dependencies:**
```bash
pip install -r requirements.txt

```


3. **Set Environment Variables:**
```bash
export HF_TOKEN="your_huggingface_token_here"

```


4. **Run the application:**
```bash
python data_processing.py
streamlit run app.py

```



### Streamlit Cloud Deployment

1. Push the code to GitHub.
2. Connect your repository to **Streamlit Cloud**.
3. In the App settings, add your `HF_TOKEN` under **Secrets**:
```toml
HF_TOKEN = "hf_xxx..."

```



---

## 🔍 About the Simulation Model

**Capacity does not change instantly.** Hugo models supply chain physics accurately:

* **Capacity:** Fixed immediate potential based on current stock.
* **Demand Spike:** Increases the rate of inventory depletion.
* **Outcome:** Hugo predicts the exact "point of failure" rather than just showing a percentage increase.

---

## 🧪 Data Source & Disclaimer

* All data used is provided by the hackathon organizers.
* The dataset is used strictly for analysis and demonstration purposes.
* No external, proprietary, or personally identifiable data (PII) is introduced, ensuring fairness and reproducibility.

---

## 👤 Authors

Developed with ❤️ by **Aatifa Risvi** and **Lakshya Varshney** as part of a hackathon-based AI procurement intelligence project.

## 📄 License

This project is licensed under the **MIT License**.

---
