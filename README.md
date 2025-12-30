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

* Computes maximum buildable units per model based on real-time Bill of Materials (BOM) dependencies.
* Highlights specific capacity-limiting components to guide procurement priority.

### ⚠️ Bottleneck Detection

* Identifies "blocker" parts that delay production.
* Categorizes issues into inventory shortages, assembly constraints, or supplier-side delays.

### 🏭 Supplier Risk Intelligence

* **Unstructured Data Parsing:** Analyzes supplier emails (`.eml`) to extract operational signals.
* **Signal Detection:** Automatically flags delays, price hikes, and quality alerts, linking them to specific production impacts.

### 🔮 Demand Spike Simulation

* **Real-world Modeling:** Hugo models risk evolution, scaling consumption rates to show how quickly "Days of Cover" deplete and when new bottlenecks will emerge.

### 💬 AI Reasoning ("Ask Hugo")

* Natural-language Q&A over live operational context.
* Provides structured root-cause analysis and actionable mitigation steps using a supported Hugging Face model.

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
* **AI/LLM:** Hugging Face Inference API (supported model like `tiiuae/falcon-7b-instruct`)  
* **Data Science:** Pandas, NumPy  
* **Visualization:** Plotly  
* **Deployment:** Streamlit Cloud (Fully cloud-native)  

---

## ⚙️ Installation & Usage

### Local Setup (Windows / Mac / Linux)

1. **Clone the repository:**

```bash
git clone https://github.com/your-username/hugo-ai-procurement-agent.git
cd hugo-ai-procurement-agent
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Run the application:

bash
Copy code
python data_processing.py       # Prepare operational snapshot
streamlit run app.py            # Launch interactive dashboard
⚠️ Note: To enable AI reasoning, set your Hugging Face token via your OS environment variables or Streamlit secrets (without committing it).

Windows (PowerShell):

powershell
Copy code
$env:HF_TOKEN="your_huggingface_token_here"
Windows (Command Prompt):

cmd
Copy code
set HF_TOKEN=your_huggingface_token_here
Mac / Linux:

bash
Copy code
export HF_TOKEN="your_huggingface_token_here"
Streamlit Cloud: Add your token in Settings → Secrets; do not commit it.

🔍 About the Simulation Model
Capacity does not change instantly. Hugo models supply chain physics accurately:

Capacity: Fixed immediate potential based on current stock.

Demand Spike: Increases the rate of inventory depletion.

Outcome: Hugo predicts the exact "point of failure" rather than just showing a percentage increase.

🧪 Data Source & Disclaimer
All data is provided by hackathon organizers.

Dataset is strictly for analysis and demonstration purposes.

No external, proprietary, or personally identifiable data (PII) is introduced.

👤 Authors
Developed with ❤️ by Aatifa Rizvi and Lakshya Varshney for hackathon-based AI procurement intelligence projects.

📄 License
This project is licensed under the MIT License.
