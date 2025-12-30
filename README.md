# 🛵 Hugo – AI Procurement Agent

**Hugo** is an AI-powered procurement and supply-chain intelligence agent. It bridges the gap between raw operational data and strategic decision-making by combining **deterministic rule-based logic** with **LLM-driven reasoning**.

Designed for hackathons and real-world operational scenarios, Hugo analyzes production capacity, detects hidden bottlenecks, assesses supplier risks from unstructured data, and simulates the impact of demand spikes.

---

## 🚀 Live Demo

🔗 **Streamlit App:**  
https://r8e5jzllm2al3svjd3wqf8.streamlit.app/

---

## 🎯 Target Audience

- **🏆 Hackathon Judges:** Evaluate problem-solving depth and data utilization  
- **👨‍💻 Technical Evaluators:** Review the hybrid AI + rule-based architecture  
- **📊 Supply-Chain Enthusiasts:** Explore digital twin–style simulations  

---

## ✨ Key Features

### 📊 Production Capacity Analysis
- Computes maximum buildable units per scooter model using real-time **Bill of Materials (BOM)** constraints
- Highlights capacity-limiting components to guide procurement priorities

### ⚠️ Bottleneck Detection
- Identifies blocker parts that restrict production or assembly
- Classifies issues into inventory shortages, assembly constraints, or supplier delays

### 🏭 Supplier Risk Intelligence
- Parses unstructured supplier emails (`.eml`)
- Automatically flags delay signals, risk language, price hikes, and quality alerts
- Links supplier risk directly to impacted scooter models

### 🔮 Demand Spike Simulation
- Models real-world supply chain physics
- Scales consumption rates to show **Days of Cover depletion**
- Predicts the **exact point of failure**, not just percentage impact

### 💬 AI Reasoning – “Ask Hugo”
- Natural-language Q&A over live operational context
- Produces root-cause analysis and actionable mitigation strategies using Hugging Face LLMs

---

## 🧠 System Architecture

Hugo uses a **Hybrid Intelligence** design for reliability and explainability:

1. **Data Processing Layer** (`data_processing.py`)  
   Converts raw data into `operational_snapshot.json`
2. **Engine Layer**  
   Capacity, Bottleneck, Supplier Risk, and Automation engines
3. **Reasoning Layer**  
   Hugging Face Inference API for high-level reasoning
4. **UI Layer**  
   Streamlit dashboard for analytics, alerts, and simulation

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit  
- **Language:** Python 3.x  
- **AI / LLM:** Hugging Face Inference API  
  (`mistralai/Mistral-7B-Instruct-v0.2:featherless-ai`)
- **Data Science:** Pandas, NumPy  
- **Visualization:** Plotly  
- **Deployment:** Streamlit Cloud  

---

## ⚙️ Installation & Usage

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/AatifaRizvi/hugo-ai-procurement-agent.git
cd hugo-ai-procurement-agent
Install dependencies

bash
Copy code
pip install -r requirements.txt
Set Environment Variable (Hugging Face Token)

Mac / Linux

bash
Copy code
export HF_TOKEN="your_token_here"
Windows (CMD)

cmd
Copy code
set HF_TOKEN=your_token_here
Windows (PowerShell)

powershell
Copy code
$env:HF_TOKEN="your_token_here"
Run the application

bash
Copy code
python data_processing.py
streamlit run app.py
🔍 Simulation Logic
Hugo models supply chain behavior realistically:

Static Capacity: Immediate build potential based on inventory

Demand Spike: Accelerated consumption rate

Outcome: Predicts time-to-failure, not just scaled output

🧪 Data & Disclaimer
All data is provided by hackathon organizers

Used strictly for demonstration and evaluation

No external, proprietary, or personally identifiable data (PII)

👤 Authors
Developed with ❤️ by
Aatifa Rizvi & Lakshya Varshney

📄 License
This project is licensed under the MIT License.
