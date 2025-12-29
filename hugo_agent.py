import json
from pathlib import Path

# Optional Ollama import
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

from agents.capacity_engine import CapacityEngine
from agents.bottleneck_engine import BottleneckEngine
from agents.supplier_engine import SupplierEngine
from agents.automation_engine import AutomationEngine

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

def load_json(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

class HugoAgent:
    def __init__(self):
        # Load data
        self.snapshot = load_json(OUTPUT_DIR / "operational_snapshot.json")
        self.model_dependencies = load_json(OUTPUT_DIR / "model_dependencies.json")
        self.email_events = load_json(OUTPUT_DIR / "email_events.json")
        self.bom_quantities = load_json(OUTPUT_DIR / "model_bom_quantities.json")
        self.assembly_constraints = load_json(OUTPUT_DIR / "assembly_constraints.json")

        # Engines
        self.capacity_engine = CapacityEngine(
            self.snapshot, self.model_dependencies, self.bom_quantities
        )
        self.capacity_report = self.capacity_engine.compute_capacity()

        self.bottleneck_engine = BottleneckEngine(
            self.snapshot, self.capacity_report, self.assembly_constraints
        )
        self.bottlenecks = self.bottleneck_engine.analyze_bottlenecks()

        self.supplier_engine = SupplierEngine(
            self.email_events, self.bottlenecks
        )

        self.automation_engine = AutomationEngine(self.snapshot)

    # --------------------------------------------------
    def compute_context(self):
        return {
            "capacity_report": self.capacity_report,
            "bottlenecks": self.bottlenecks,
            "supplier_report": self.supplier_engine.analyze_suppliers(),
            "alerts": self.automation_engine.run_automation()
        }

    # --------------------------------------------------
    def rule_based_answer(self, question, ctx):
        q = question.lower()

        # Production capacity questions
        if any(x in q for x in ["how many", "capacity", "build", "produce"]):
            lines = [
                f"- {m}: {v['max_buildable_units']} units"
                for m, v in ctx["capacity_report"].items()
            ]
            return "📦 **Production Capacity**\n\n" + "\n".join(lines), "High"

        # Bottleneck questions
        if any(x in q for x in ["bottleneck", "break", "delay"]):
            if not ctx["bottlenecks"]:
                return "No bottlenecks detected.", "High"

            lines = [
                f"- {b['part']} impacts {b['model']} ({b['reason']})"
                for b in ctx["bottlenecks"]
            ]
            return "⚠️ **Bottlenecks Detected**\n\n" + "\n".join(lines), "High"

        # Supplier risk questions
        if any(x in q for x in ["supplier", "vendor", "risk"]):
            risky = [s for s in ctx["supplier_report"] if s["risk_level"] != "Low"]
            if not risky:
                return "All suppliers are stable.", "Medium"

            lines = [
                f"- {s['supplier']} (Risk: {s['risk_level']})"
                for s in risky
            ]
            return "🏭 **Supplier Risk**\n\n" + "\n".join(lines), "Medium"

        return None, None

    # --------------------------------------------------
    def llm_answer(self, question, ctx):
        if not OLLAMA_AVAILABLE:
            return (
                "LLM reasoning is not available right now.\n\n"
                "**Confidence:** Low"
            )

        prompt = f"""
    You are an AI procurement analyst.

    Answer the user's question using ONLY the provided context.

    When answering:
- Group parts by common root causes
- Explain why those causes are occurring
- Highlight which causes are most critical
- Do not simply list parts

After your answer, add:
Confidence: High / Medium / Low

USER QUESTION:
{question}

CONTEXT:
{json.dumps(ctx, indent=2)}

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

    # --------------------------------------------------
    def ask(self, question):
        ctx = self.compute_context()

        # 1️⃣ Try fast rule-based
        answer, confidence = self.rule_based_answer(question, ctx)
        if answer:
            return f"{answer}\n\n**Confidence:** {confidence}"

        # 2️⃣ Otherwise use LLM
        try:
            if OLLAMA_AVAILABLE:
                return self.llm_answer(question, ctx)
            else:
                return (
                    "This question requires deeper reasoning.\n\n"
                    "Please start Ollama to enable AI responses.\n\n"
                    "THis error indicates that the Ollama library is not installed or Ollama is not running.\n\n"
                    "**Confidence:** Low"
                )
        except Exception:
            return (
                "I could not generate an AI response right now.\n\n"
                "**Confidence:** Low"
            )

    # --------------------------------------------------
    def run_full_analysis(self):
        return f"""
### 📊 System Overview

• Models analyzed: {len(self.capacity_report)}
• Bottlenecks detected: {len(self.bottlenecks)}
• Active alerts: {len(self.automation_engine.run_automation())}

Overall system is stable, but supplier risks should be monitored.
"""
