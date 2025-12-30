import json
import os
from pathlib import Path
from huggingface_hub import InferenceClient
import streamlit as st
from agents.capacity_engine import CapacityEngine
from agents.bottleneck_engine import BottleneckEngine
from agents.supplier_engine import SupplierEngine
from agents.automation_engine import AutomationEngine

# --------------------------------------------------
# Configuration
# --------------------------------------------------
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

# --------------------------------------------------
# HF TOKEN LOADER
# --------------------------------------------------
def get_hf_token():
    # Streamlit Cloud
    if "HF_TOKEN" in st.secrets:
        return st.secrets["HF_TOKEN"]

    # Local environment
    return os.getenv("HF_TOKEN")

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)



class HugoAgent:
    def __init__(self):
        # ---------------- Load Data ----------------
        self.snapshot = load_json(OUTPUT_DIR / "operational_snapshot.json")
        self.model_dependencies = load_json(OUTPUT_DIR / "model_dependencies.json")
        self.email_events = load_json(OUTPUT_DIR / "email_events.json")
        self.bom_quantities = load_json(OUTPUT_DIR / "model_bom_quantities.json")
        self.assembly_constraints = load_json(OUTPUT_DIR / "assembly_constraints.json")

        # ---------------- Engines ----------------
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

        # ---------------- HF Client ----------------
        self.client = None
        token = get_hf_token()
        if token:
            self.client = InferenceClient(
                model=HF_MODEL,
                token=token
            )

    # --------------------------------------------------
    def compute_context(self):
        return {
            "capacity_report": self.capacity_report,
            "bottlenecks": self.bottlenecks,
            "supplier_report": self.supplier_engine.analyze_suppliers(),
            "alerts": self.automation_engine.run_automation(),
        }

    # --------------------------------------------------
    # RULE-BASED ANSWERS (FAST + DETERMINISTIC)
    # --------------------------------------------------
    def rule_based_answer(self, question, ctx):
        q = question.lower()

        if any(x in q for x in ["how many", "capacity", "build", "produce"]):
            lines = [
                f"- {m}: {v.get('max_buildable_units', 'N/A')} units"
                for m, v in ctx["capacity_report"].items()
            ]
            return "📦 Production Capacity\n\n" + "\n".join(lines), "High"

        if any(x in q for x in ["bottleneck", "delay", "break"]):
            if not ctx["bottlenecks"]:
                return "No critical bottlenecks detected.", "High"

            lines = [
                f"- {b.get('part', 'Unknown')} impacts {b.get('model', 'N/A')} "
                f"({b.get('reason', 'constraint')})"
                for b in ctx["bottlenecks"]
            ]
            return "⚠️ Bottlenecks Detected\n\n" + "\n".join(lines), "High"

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
            return "🏭 Supplier Risk\n\n" + "\n".join(lines), "Medium"

        return None, None

    # --------------------------------------------------
    # LLM ANSWER (LOCAL ONLY)
    # --------------------------------------------------
    def llm_answer(self, question, ctx):
        if not self.client:
            return (
                "AI reasoning disabled (HF_TOKEN missing).\n\n"
                "Confidence: Low"
            )

        system_prompt = (
    "You are a senior procurement and supply-chain intelligence analyst. "
    "You specialize in capacity planning, inventory risk, and root-cause analysis. "
    "You must perform structured, evidence-based reasoning using ONLY the provided context. "
    "Think analytically, avoid generic summaries, and prioritize operational decision-making. "
    "If multiple issues share the same failure mechanism, treat them as one systemic issue."
)


        user_prompt = f"""
Analyze the procurement and production situation using ONLY the context below.

You MUST follow the exact structure and rules defined here.

────────────────────────────────
1. ROOT CAUSE ANALYSIS
────────────────────────────────
Identify 2-4 DISTINCT root causes (not symptoms).

For EACH root cause:
- Clearly describe what is happening
- Identify the affected parts and/or models
- Explain WHY this issue exists using evidence from the context
  (e.g., missing purchase orders, supplier inactivity, BOM dependency,
   assembly constraints, capacity limits)

If multiple parts fail for the same reason, group them under one root cause.
Do NOT list parts without explaining the mechanism behind the failure.

────────────────────────────────
2. IMPACT ASSESSMENT
────────────────────────────────
For EACH root cause, explain:
- Which production models are impacted
- Whether the impact is:
  • Immediate (0-3 days)
  • Short-term (4-14 days)
  • Medium-term (weeks)
- Whether the constraint is:
  • Capacity-limiting
  • Assembly-limiting
  • Supplier-risk-driven

Tie impact explicitly to operational outcomes
(e.g., inability to build units, stalled assemblies, delayed deliveries).

────────────────────────────────
3. CRITICAL RISK PRIORITIZATION
────────────────────────────────
Rank the risks from MOST critical to LEAST critical.

For EACH ranked risk, justify the priority using:
- Days of cover / inventory runway
- Breadth of dependency (how many models or assemblies are affected)
- Lack of near-term mitigation (e.g., no upcoming POs, single supplier)

Do NOT rank risks without justification.

────────────────────────────────
4. ACTIONABLE MITIGATION PLAN
────────────────────────────────
For EACH root cause, propose concrete and operational actions.

Examples of acceptable actions:
- Expedite or place purchase orders for specific parts
- Reallocate inventory between models
- Introduce alternate suppliers or temporary substitutes
- Adjust production sequencing to protect high-priority models

Avoid generic advice like “monitor closely” or “improve planning.”

────────────────────────────────
RULES (NON-NEGOTIABLE)
────────────────────────────────
- Use ONLY the provided context
- Do NOT invent numbers, timelines, or causes
- Do NOT restate the context verbatim
- Do NOT give high-level summaries without analysis
- Every claim must be logically supported by the context

QUESTION:
{question}

CONTEXT:
{json.dumps(ctx, indent=2)}

End your response with EXACTLY:
Confidence: High / Medium / Low
"""


        response = self.client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=300,
            temperature=0.2,
        )

        return response.choices[0].message.content

    # --------------------------------------------------
    # ASK HUGO (BULLETPROOF)
    # --------------------------------------------------
    def ask(self, question):
        ctx = self.compute_context()

        # Rule-based fast path
        answer, confidence = self.rule_based_answer(question, ctx)
        if answer:
            return f"{answer}\n\nConfidence: {confidence}"

        # AI reasoning path
        try:
            return self.llm_answer(question, ctx)
        except Exception as e:
            return (
                "AI reasoning temporarily unavailable.\n\n"
                f"Error: {repr(e)}\n\n"
                "Confidence: Low"
            )

    # --------------------------------------------------
    # ANALYTICS TAB
    # --------------------------------------------------
    def run_full_analysis(self):
        return f"""
System Overview

• Models analyzed: {len(self.capacity_report)}
• Bottlenecks detected: {len(self.bottlenecks)}
• Active alerts: {len(self.automation_engine.run_automation())}

Overall system is stable; supplier risks should be monitored.
"""
    def simulate_demand_spike(self, spike_percent: int):
        """
        Recompute operational risk under increased demand.
        Demand affects consumption rate, not instantaneous capacity.
        """

        multiplier = 1 + spike_percent / 100

        # Deep copy snapshot (list of parts)
        simulated_snapshot = json.loads(json.dumps(self.snapshot))

        for part in simulated_snapshot:
            if part.get("avg_daily_consumption", 0) > 0:
                part["avg_daily_consumption"] = round(
                    part["avg_daily_consumption"] * multiplier, 2
                )

            # Recompute days of cover
            if part["avg_daily_consumption"] > 0:
                part["days_of_cover"] = round(
                    part["on_hand"] / part["avg_daily_consumption"], 2
                )
            else:
                part["days_of_cover"] = float("inf")

        # Capacity does NOT change immediately (this is correct)
        sim_capacity_engine = CapacityEngine(
            simulated_snapshot,
            self.model_dependencies,
            self.bom_quantities
        )
        sim_capacity_report = sim_capacity_engine.compute_capacity()

        sim_bottleneck_engine = BottleneckEngine(
            simulated_snapshot,
            sim_capacity_report,
            self.assembly_constraints
        )
        sim_bottlenecks = sim_bottleneck_engine.analyze_bottlenecks()

        return sim_capacity_report, sim_bottlenecks, simulated_snapshot
