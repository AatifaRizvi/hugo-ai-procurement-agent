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
BOM_QTY_FILE = OUTPUT_DIR / "model_bom_quantities.json"
ASSEMBLY_FILE = OUTPUT_DIR / "assembly_constraints.json"

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
        self.snapshot = load_json(SNAPSHOT_FILE)
        self.model_dependencies = load_json(MODEL_DEPS_FILE)
        self.email_events = load_json(EMAIL_EVENTS_FILE)
        self.bom_quantities = load_json(BOM_QTY_FILE)
        self.assembly_constraints = load_json(ASSEMBLY_FILE)

        self.capacity_engine = CapacityEngine(
            self.snapshot,
            self.model_dependencies,
            self.bom_quantities
        )
        self.capacity_report = self.capacity_engine.compute_capacity()

        self.bottleneck_engine = BottleneckEngine(
            self.snapshot,
            self.capacity_report,
            self.assembly_constraints
        )
        self.bottlenecks = self.bottleneck_engine.analyze_bottlenecks()

        self.supplier_engine = SupplierEngine(
            self.email_events,
            self.bottlenecks
        )

        self.automation_engine = AutomationEngine(self.snapshot)

    def compute_context(self):
        return {
            "capacity_report": self.capacity_report,
            "bottlenecks": self.bottlenecks,
            "supplier_report": self.supplier_engine.analyze_suppliers(),
            "alerts": self.automation_engine.run_automation(),
            "assembly_constraints": self.assembly_constraints
        }

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

    def run_full_analysis(self):
        return run_llm(self.compute_context())
