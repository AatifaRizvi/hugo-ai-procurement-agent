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

BASE_DIR = Path(__file__).resolve().parent.parent
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
# MAIN AGENT
# =====================================================

def run_hugo():
    # -----------------------------
    # Load preprocessed truth
    # -----------------------------
    snapshot = load_json(SNAPSHOT_FILE)
    model_dependencies = load_json(MODEL_DEPS_FILE)
    email_events = load_json(EMAIL_EVENTS_FILE)

    # -----------------------------
    # Deterministic engines
    # -----------------------------
    capacity_engine = CapacityEngine(snapshot, model_dependencies)
    capacity_report = capacity_engine.compute_capacity()

    bottleneck_engine = BottleneckEngine(snapshot, capacity_report)
    bottlenecks = bottleneck_engine.analyze_bottlenecks()

    supplier_engine = SupplierEngine(email_events, bottlenecks)
    supplier_report = supplier_engine.analyze_suppliers()

    automation_engine = AutomationEngine(snapshot)
    alerts = automation_engine.run_automation()

    # -----------------------------
    # Reasoning context
    # -----------------------------
    reasoning_context = {
        "capacity_report": capacity_report,
        "bottlenecks": bottlenecks,
        "supplier_report": supplier_report,
        "alerts": alerts
    }

    # -----------------------------
    # LLM reasoning
    # -----------------------------
    explanation = run_llm(reasoning_context)

    print("\n HUGO – PROCUREMENT INTELLIGENCE\n")
    print(explanation)

    print("\n AUTOMATION ALERTS\n")
    for alert in alerts:
        print("-", alert)

# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == "__main__":
    run_hugo()
