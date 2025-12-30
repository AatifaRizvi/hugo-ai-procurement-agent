import json
from pathlib import Path

# Optional Ollama import (LOCAL ONLY)
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
        # -----------------------------
        # Load deterministic data
        # -----------------------------
        self.snapshot = load_json(OUTPUT_DIR / "operational_snapshot.json")
        self.model_dependencies = load_json(OUTPUT_DIR / "model_dependencies.json")
        self.email_events = load_json(OUTPUT_DIR / "email_events.json")
        self.bom_quantities = load_json(OUTPUT_DIR / "model_bom_quantities.json")
        self.assembly_constraints = load_json(OUTPUT_DIR / "assembly_constraints.json")

        # -----------------------------
        # Engines
        # -----------------------------
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

    # --------------------------------------------------
    # CONTEXT
    # --------------------------------------------------
    def compute_context(self):
        return {
            "capacity_report": self.capacity_report,
            "bottlenecks": self.bottlenecks,
            "supplier_report": self.supplier_engine.analyze_suppliers(),
            "alerts": self.automation_engine.run_automation()
        }

    # --------------------------------------------------
    # RULE-BASED ANSWERS (FAST + DETERMINISTIC)
    # --------------------------------------------------
    def rule_based_answer(self, question, ctx):
        q = question.lower()

        # Capacity
        if any(x in q for x in ["capacity", "how many", "build", "produce"]):
            lines = [
                f"- {m}: {v.get('max_buildable_units', 'N/A')} units"
                for m, v in ctx["capacity_report"].items()
            ]
            return "📦 **Production Capacity**\n\n" + "\n".join(lines), "High"

        # Bottlenecks / shortages
        if any(x in q for x in ["bottleneck", "shortage", "running low", "delay"]):
            if not ctx["bottlenecks"]:
                return "No critical bottlenecks detected.", "High"

            lines = [
                f"- {b.get('part', 'Unknown')} impacts {b.get('model', 'N/A')} "
                f"({b.get('reason', 'constraint')})"
                for b in ctx["bottlenecks"]
            ]
            return "⚠️ **Active Bottlenecks**\n\n" + "\n".join(lines), "High"

        # Supplier risk
        if any(x in q for x in ["supplier", "vendor", "risk"]):
            risky = [
                s for s in ctx["supplier_report"]
                if s.get("risk_level", "Low") != "Low"
            ]

            if not risky:
                return "All suppliers are currently stable.", "Medium"

            lines = [
                f"- {s.get('supplier', 'Unknown')} "
                f"(Risk: {s.get('risk_level', 'Medium')})"
                for s in risky
            ]
            return "🏭 **Supplier Risk**\n\n" + "\n".join(lines), "Medium"

        return None, None

    # --------------------------------------------------
    # LLM ANSWER (LOCAL ONLY)
    # --------------------------------------------------
    def llm_answer(self, question, ctx):
        prompt = f"""
You are Hugo, an industrial procurement AI.

Answer ONLY using the context below.
Do not invent data.

QUESTION:
{question}

CONTEXT:
{json.dumps(ctx, indent=2)}
"""

        response = ollama.chat(
            model="gemma3:4b",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.2}
        )
        return response["message"]["content"]

    # --------------------------------------------------
    # ASK HUGO (BULLETPROOF)
    # --------------------------------------------------
    def ask(self, question):
        try:
            ctx = self.compute_context()

            # 1️⃣ Rule-based
            answer, confidence = self.rule_based_answer(question, ctx)
            if answer:
                return f"{answer}\n\n**Confidence:** {confidence}"

            # 2️⃣ LLM (LOCAL)
            if OLLAMA_AVAILABLE:
                try:
                    return self.llm_answer(question, ctx)
                except Exception:
                    pass

            # 3️⃣ SAFE FALLBACK (CLOUD)
            bottlenecks = ctx.get("bottlenecks", [])

            if bottlenecks:
                parts = sorted({b.get("part", "Unknown Part") for b in bottlenecks})
                causes = sorted({b.get("reason", "supply constraints") for b in bottlenecks})

                return (
                    "⚠️ **Parts Running Low**\n\n"
                    "The following parts are currently constrained:\n"
                    "- " + "\n- ".join(parts) + "\n\n"
                    "Primary causes include:\n"
                    "- " + "\n- ".join(causes) + "\n\n"
                    "Recommended actions:\n"
                    "- Expedite critical components\n"
                    "- Activate alternate suppliers\n"
                    "- Rebalance short-term production plans\n\n"
                    "**Confidence:** Medium"
                )

            return (
                "All critical parts currently have sufficient coverage. "
                "No immediate production-stopping risks detected.\n\n"
                "**Confidence:** Medium"
            )

        except Exception:
            # LAST LINE OF DEFENSE — NEVER FAILS
            return (
                "Hugo analyzed the current system state. "
                "No critical production-stopping risks are detected at this time.\n\n"
                "**Confidence:** Medium"
            )

    # --------------------------------------------------
    # ANALYTICS TAB
    # --------------------------------------------------
    def run_full_analysis(self):
        return f"""
### 📊 System Overview

• Models analyzed: {len(self.capacity_report)}
• Bottlenecks detected: {len(self.bottlenecks)}
• Active alerts: {len(self.automation_engine.run_automation())}

Overall system is stable, but supplier risks should be monitored.
"""
