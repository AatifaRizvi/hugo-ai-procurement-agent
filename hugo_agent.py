# agents/hugo_agent.py

import json
from pathlib import Path
import ollama

from agents.capacity_engine import CapacityEngine
from agents.bottleneck_engine import BottleneckEngine
from agents.supplier_engine import SupplierEngine
from agents.automation_engine import AutomationEngine

# =====================================================
# PATH CONFIG
# =====================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

SNAPSHOT_FILE = OUTPUT_DIR / "operational_snapshot.json"
MODEL_DEPS_FILE = OUTPUT_DIR / "model_dependencies.json"
EMAIL_EVENTS_FILE = OUTPUT_DIR / "email_events.json"

# =====================================================
# HELPERS
# =====================================================

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_llm(context):
    prompt = f"""
You are an AI procurement analyst.

Use the following structured analysis to explain:
- What is going wrong
- Why it is happening
- What actions should be taken

Rules:
- Do not invent data
- Do not calculate numbers
- Use only the provided context

CONTEXT:
{json.dumps(context, indent=2)}

Respond clearly and concisely.
"""

    response = ollama.chat(
        model="gemma3:4b",
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.2}
    )

    return response["message"]["content"]

# =====================================================
# HUGO AGENT CLASS
# =====================================================

class HugoAgent:
    def __init__(self):
        # Load data
        self.snapshot = load_json(SNAPSHOT_FILE)
        self.model_dependencies = load_json(MODEL_DEPS_FILE)
        self.email_events = load_json(EMAIL_EVENTS_FILE)

        # Initialize deterministic engines
        self.capacity_engine = CapacityEngine(self.snapshot, self.model_dependencies)
        self.bottleneck_engine = BottleneckEngine(self.snapshot, self.capacity_engine.compute_capacity())
        self.supplier_engine = SupplierEngine(self.email_events, self.bottleneck_engine.analyze_bottlenecks())
        self.automation_engine = AutomationEngine(self.snapshot)

    def compute_context(self):
        # Build full reasoning context
        capacity_report = self.capacity_engine.compute_capacity()
        bottlenecks = self.bottleneck_engine.analyze_bottlenecks()
        supplier_report = self.supplier_engine.analyze_suppliers()
        alerts = self.automation_engine.run_automation()

        context = {
            "capacity_report": capacity_report,
            "bottlenecks": bottlenecks,
            "supplier_report": supplier_report,
            "alerts": alerts
        }

        return context

    def ask(self, user_question):
        context = self.compute_context()

        prompt = f"""
You are an AI procurement analyst.

Answer the user's question using ONLY the provided context.
If the answer cannot be determined, say so explicitly.

USER QUESTION:
{user_question}

CONTEXT:
{json.dumps(context, indent=2)}

Rules:
- Do not invent data
- Do not perform calculations
- Be precise and actionable
"""

        response = ollama.chat(
            model="gemma3:4b",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.2}
        )

        return response["message"]["content"]

    # run full Hugo reasoning
    def run_full_analysis(self):
        context = self.compute_context()
        explanation = run_llm(context)
        return explanation
