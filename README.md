🛵 Hugo – AI Procurement Agent
-----------------------------------
Hugo is an AI-powered procurement and supply-chain intelligence agent. It bridges the gap between raw operational data and strategic decision-making by combining deterministic rule-based logic with LLM-driven reasoning.

Designed for AMULATE Hackathon and real-world operational scenarios, Hugo analyzes production capacity, detects hidden bottlenecks, assesses supplier risks from unstructured data, and simulates the impact of demand spikes.

🎯 Target Audience
----------------------
🏆 Hackathon Judges: For evaluating problem-solving and data utilization.

👨‍💻 Technical Evaluators: For reviewing the hybrid AI architecture.

📊 Supply-Chain Enthusiasts: For exploring digital twin simulations.

✨ Key Features
------------------------
📊 Production Capacity Analysis
Computes maximum buildable units per model based on real-time Bill of Materials (BOM) dependencies.

Highlights specific capacity-limiting components to guide procurement priority.

⚠️ Bottleneck Detection
Identifies "blocker" parts that delay production.

Categorizes issues into inventory shortages, assembly constraints, or supplier-side delays.

🏭 Supplier Risk Intelligence
Unstructured Data Parsing: Analyzes supplier emails (.eml) to extract operational signals.

Signal Detection: Automatically flags delays, price hikes, and quality alerts.

🔮 Demand Spike Simulation
Hugo models "Days of Cover" depletion to predict the exact "point of failure" rather than just simple scaling.

💬 AI Reasoning ("Ask Hugo")
Natural-language Q&A using Mistral-7B for root-cause analysis and actionable mitigation steps.

🧠 System Architecture
----------------------------
Data Processing Layer: (data_processing.py) Transforms raw data into operational_snapshot.json.

Engine Layer: Logic engines for Capacity, Bottlenecks, and Supplier Risk.

Reasoning Layer: Hugging Face Inference API for high-level insight.

UI Layer: Streamlit dashboard for interactive analytics.

🛠️ Tech Stack
-------------------
Frontend: Streamlit

AI/LLM: Hugging Face Inference API (Mistral-7B-Instruct-v0.2)

Data Science: Pandas, NumPy, Plotly

⚙️ Installation & Usage
----------------------------
1. Clone the repository
Bash

git clone https://github.com/AatifaRizvi/hugo-ai-procurement-agent.git
cd hugo-ai-procurement-agent
2. Install dependencies
Bash

pip install -r requirements.txt
3. Set Environment Variables (Secret Key)
Hugo require a Hugging Face Token (HF_TOKEN) to power the AI reasoning. Follow the command for your specific Operating System:

🪟 For Windows Users
Option A (PowerShell - Recommended):

PowerShell

$env:HF_TOKEN="your_huggingface_token_here"
Option B (Command Prompt):

DOS

set HF_TOKEN=your_huggingface_token_here
🍎 For Mac / 🐧 Linux Users
Bash

export HF_TOKEN="your_huggingface_token_here"
Pro Tip: You can also create a .env file in the root directory and add HF_TOKEN=your_token_here to avoid setting it every time.

4. Run the application
Bash

python data_processing.py
streamlit run app.py
🚀 Streamlit Cloud Deployment
Push your code to GitHub.

Connect your repository to Streamlit Cloud.

Go to Settings > Secrets and add your token:

Ini, TOML

HF_TOKEN = "hf_xxx..."
🔍 About the Simulation Model
Capacity does not change instantly. Hugo models supply chain physics accurately:

Capacity: Fixed immediate potential based on current stock.

Demand Spike: Increases the rate of inventory depletion.

Outcome: Hugo predicts the exact "point of failure" during a spike.

🧪 Data Source & Disclaimer
--------------------------------
All data used is provided by the hackathon organizers.

No external, proprietary, or personally identifiable data (PII) is introduced, ensuring fairness and reproducibility.

👤 Authors
-----------------
Developed with ❤️ by Aatifa Rizvi and Lakshya Varshney for the AI Procurement Intelligence Hackathon.

📄 License
This project is licensed under the MIT License.
