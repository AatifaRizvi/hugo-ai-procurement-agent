import json
import os
from pathlib import Path
from openai import OpenAI
import streamlit as st
from agents.capacity_engine import CapacityEngine
from agents.bottleneck_engine import BottleneckEngine
from agents.supplier_engine import SupplierEngine
from agents.automation_engine import AutomationEngine


# ======================================================
# CONFIG
# ======================================================
HF_ROUTER_BASE = "https://router.huggingface.co/v1"
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2:featherless-ai"


# ======================================================
# HUGO AGENT
# ======================================================
class HugoAgent:
    def __init__(self):
        # ---------------- Load Data ----------------
        base_dir = Path(__file__).resolve().parent
        out = base_dir / "outputs"

        self.snapshot = json.load(open(out / "operational_snapshot.json"))
        self.model_dependencies = json.load(open(out / "model_dependencies.json"))
        self.email_events = json.load(open(out / "email_events.json"))
        self.bom_quantities = json.load(open(out / "model_bom_quantities.json"))
        self.assembly_constraints = json.load(open(out / "assembly_constraints.json"))

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

        # ---------------- HF Router Client ----------------
        token = st.secrets.get("HF_TOKEN") or os.getenv("HF_TOKEN")
        if not token:
            raise RuntimeError("HF_TOKEN not set")

        self.client = OpenAI(
            base_url=HF_ROUTER_BASE,
            api_key=token,
        )

    # --------------------------------------------------
    def compute_context(self):
        return {
            "capacity_report": self.capacity_report,
            "bottlenecks": self.bottlenecks,
            "supplier_report": self.supplier_engine.analyze_suppliers(),
            "alerts": self.automation_engine.run_automation(),
            "email_events": self.email_events,
            "snapshot": self.snapshot,
        }

    # --------------------------------------------------
    # RULE-BASED ANSWERS
    # --------------------------------------------------
    def rule_based_answer(self, question, ctx):
        q = question.lower()

        if any(x in q for x in ["capacity", "build", "produce"]):
            lines = [
                f"- {m}: {v.get('max_buildable_units', 'N/A')} units"
                for m, v in ctx["capacity_report"].items()
            ]
            return "📦 Production Capacity\n\n" + "\n".join(lines), "High"

        if "bottleneck" in q:
            if not ctx["bottlenecks"]:
                return "No critical bottlenecks detected.", "High"

            lines = [
                f"- {b['part']} impacts {b['model']} ({b['reason']})"
                for b in ctx["bottlenecks"]
            ]
            return "⚠️ Bottlenecks\n\n" + "\n".join(lines), "High"

        return None, None

    # --------------------------------------------------
    # LLM ANSWER (HF ROUTER)
    # --------------------------------------------------
    def llm_answer(self, question, ctx):
        
        prompt = f"""
You are acting as a Senior Procurement, Supply Chain, and Operations
Intelligence Analyst advising executive leadership.

You must perform a DEEP, EVIDENCE-DRIVEN analysis using ALL the structured
signals provided below. Your analysis should integrate operational data,
capacity constraints, supplier risk, and unstructured email intelligence.

STRICT RULES:
- Use ONLY the information provided in the data below
- Do NOT invent numbers, suppliers, or timelines
- Do NOT use external knowledge
- If information is missing, explicitly state the limitation
- Every insight must be traceable to a specific signal or dataset

AVAILABLE DATA SOURCES (YOU MUST USE ALL WHERE RELEVANT):

1. Capacity Report
   - Model-wise maximum buildable units
   - Derived from BOM constraints and inventory availability

2. Bottleneck Analysis
   - Parts causing production or assembly constraints
   - Links between parts, models, and limiting factors

3. Supplier Risk Signals
   - Derived from unstructured email communications
   - Includes delay notices, shortages, escalations, or risk language

4. Automation Alerts
   - System-generated alerts based on thresholds and rules

5. Raw Email Events
   - Supplier communications containing qualitative risk indicators
   - You must extract operational meaning from these emails
   - Treat emails as early-warning signals, not confirmations

ANALYSIS OBJECTIVES:

1. Root Cause Analysis
   - Identify the primary and secondary drivers of risk
   - Explicitly connect:
     • Low inventory / days of cover
     • Capacity shortfalls
     • Bottleneck propagation
     • Supplier communications (emails)
   - Explain WHY the issues are occurring, not just WHAT is happening

2. Impact Assessment
   - Describe downstream impact on:
     • Production capacity
     • Assembly feasibility
     • Delivery timelines
     • Supplier reliability
   - Separate:
     • Immediate operational impact
     • Near-term planning impact

3. Risk Prioritization
   - Rank the most critical risks by severity and urgency
   - Justify ranking using:
     • Days of cover
     • Number of models affected
     • Presence of supplier delay or risk language in emails
     • Lack of alternate sourcing signals

4. Actionable Mitigation Strategy
   - Provide CONCRETE actions, not generic advice
   - Categorize actions into:
     • Immediate (0-2 weeks)
     • Near-term (1-2 months)
     • Strategic (long-term resilience)
   - Explicitly reference which data signal triggered each action

5. Executive Summary
   - 3-5 concise bullet points
   - Written for non-technical leadership
   - Focus on decisions that must be made now

DATA (STRUCTURED CONTEXT):
{json.dumps(ctx, indent=2)}

USER QUESTION:
{question}

RESPONSE REQUIREMENTS:
- Use clear section headings
- Use bullet points where appropriate
- Be concise but thorough
- Clearly reference data signals (capacity, bottlenecks, emails, alerts)

End your response with exactly ONE of:
Confidence: High
Confidence: Medium
Confidence: Low
"""


        try:
            completion = self.client.chat.completions.create(
                model=HF_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=2000,
            )

            return completion.choices[0].message.content

        except Exception as e:
            return (
                "AI reasoning temporarily unavailable.\n\n"
                f"Error: {repr(e)}\n\n"
                "Confidence: Low"
            )

    # --------------------------------------------------
    def ask(self, question):
        ctx = self.compute_context()

        answer, conf = self.rule_based_answer(question, ctx)
        if answer:
            return f"{answer}\n\nConfidence: {conf}"

        return self.llm_answer(question, ctx)

    # --------------------------------------------------
    # ANALYTICS
    # --------------------------------------------------
    def run_full_analysis(self):
        return f"""
System Overview

• Models analyzed: {len(self.capacity_report)}
• Bottlenecks detected: {len(self.bottlenecks)}
• Active alerts: {len(self.automation_engine.run_automation())}
"""

    # --------------------------------------------------
    # DEMAND SPIKE SIMULATION
    # --------------------------------------------------
    def simulate_demand_spike(self, spike_percent: int):
        multiplier = 1 + spike_percent / 100
        simulated_snapshot = json.loads(json.dumps(self.snapshot))

        for part in simulated_snapshot:
            if part.get("avg_daily_consumption", 0) > 0:
                part["avg_daily_consumption"] = round(
                    part["avg_daily_consumption"] * multiplier, 2
                )

            if part["avg_daily_consumption"] > 0:
                part["days_of_cover"] = round(
                    part["on_hand"] / part["avg_daily_consumption"], 2
                )
            else:
                part["days_of_cover"] = float("inf")

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
# ==================================================
