
---

# 🛵 Hugo – AI Procurement Agent

**Hugo** is an AI-powered procurement and supply-chain intelligence agent. It bridges the gap between raw operational data and strategic decision-making by combining **deterministic rule-based logic** with **LLM-driven reasoning**.

Designed for hackathons and real-world operational scenarios, Hugo analyzes production capacity, detects hidden bottlenecks, assesses supplier risks from unstructured data, and simulates the impact of demand spikes.

---

## 🎯 Target Audience

* **🏆 Hackathon Judges:** Evaluate problem-solving and data utilization.
* **👨‍💻 Technical Evaluators:** Review the hybrid AI architecture.
* **📊 Supply-Chain Enthusiasts:** Explore digital twin simulations.

---

## ✨ Key Features

### 📊 Production Capacity Analysis

* Computes maximum buildable units per model based on real-time **Bill of Materials (BOM)** dependencies.
* Highlights specific capacity-limiting components to guide procurement priority.

### ⚠️ Bottleneck Detection

* Identifies "blocker" parts that delay production.
* Categorizes issues into inventory shortages, assembly constraints, or supplier-side delays.

### 🏭 Supplier Risk Intelligence

* **Unstructured Data Parsing:** Analyzes supplier emails (`.eml`) to extract operational signals.
* **Signal Detection:** Automatically flags delays, price hikes, and quality alerts, linking them to specific production impacts.

### 🔮 Demand Spike Simulation

* **Real-world Modeling:** Hugo models risk evolution, scaling consumption rates to show how quickly "Days of Cover" deplete and when new bottlenecks emerge.

### 💬 AI Reasoning ("Ask Hugo")

* Natural-language Q&A over live operational context.
* Provides structured root-cause analysis and actionable mitigation steps using Hugging Face models.

---

## 🧠 System Architecture

Hugo uses a **Hybrid Intelligence** design to ensure speed, reliability, and transparency.

1. **Data Processing Layer:** (`data_processing.py`) Transforms raw data into a structured `operational_snapshot.json`.
2. **Engine Layer:** Dedicated engines for Capacity, Bottlenecks, and Supplier Risk.
3. **Reasoning Layer:** Hugging Face Inference API for high-level insight.
4. **UI Layer:** Streamlit dashboard for interactive analytics and simulation.

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Language:** Python 3.x
* **AI/LLM:** Hugging Face Inference API (`mistralai/Mistral-7B-Instruct-v0.2:featherless-ai`)
* **Data Science:** Pandas, NumPy
* **Visualization:** Plotly
* **Deployment:** Streamlit Cloud

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


3. **Set up your Environment Variables:**
To enable AI reasoning, you must provide a Hugging Face token.
* **Mac / Linux:** `export HF_TOKEN="your_token_here"`
* **Windows (CMD):** `set HF_TOKEN=your_token_here`
* **Windows (PowerShell):** `$env:HF_TOKEN="your_token_here"`


4. **Run the application:**
```bash
python data_processing.py      # Prepare operational snapshot
streamlit run app.py           # Launch interactive dashboard

```



---

## 🔍 Simulation Logic

Capacity does not change instantly. Hugo models supply chain physics accurately:

* **Static Capacity:** Fixed immediate potential based on current stock.
* **Demand Spike:** Increases the rate of inventory depletion.
* **Outcome:** Hugo predicts the exact **point of failure** (time-to-zero) rather than just a generic percentage increase.

---

## 🧪 Data & Disclaimer

* All data is provided by hackathon organizers.
* Dataset is strictly for analysis and demonstration purposes.
* No external, proprietary, or personally identifiable data (PII) is introduced.

---

## 👤 Authors

Developed with ❤️ by **Aatifa Rizvi** and **Lakshya Varshney** for hackathon-based AI procurement intelligence projects.

## 📄 License

This project is licensed under the MIT License.

---
