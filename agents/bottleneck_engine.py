# agents/bottleneck_engine.py

class BottleneckEngine:
    """
    Identifies bottleneck parts, explains why they are bottlenecks,
    and links them to capacity and assembly constraints.
    """

    def __init__(self, snapshot, capacity_report, assembly_constraints):
        self.snapshot = snapshot
        self.capacity_report = capacity_report
        self.assembly_constraints = assembly_constraints

    def analyze_bottlenecks(self):
        bottlenecks = []

        for part in self.snapshot:
            days = part.get("days_of_cover", float("inf"))
            on_hand = part.get("on_hand", 0)
            part_id = part.get("part_id")
            used_in_models = part.get("used_in_models", [])

            if days < 5:
                # ----------------------------
                # Severity
                # ----------------------------
                if on_hand == 0:
                    severity = "blocking"
                elif days < 2:
                    severity = "critical"
                else:
                    severity = "warning"
                if severity == "blocking":
                    priority = "P1"
                elif severity == "critical":
                    priority = "P2"
                else:
                    priority = "P3"
                # ----------------------------
                # Root cause
                # ----------------------------
                if part.get("next_po_arrival_days") is None:
                    cause = "no_inbound_supply"
                elif part.get("next_po_arrival_days", 0) > days:
                    cause = "late_replenishment"
                else:
                    cause = "demand_spike"

                # ----------------------------
                # Capacity impact
                # ----------------------------
                impacted_models = {
                    model: self.capacity_report.get(model, {})
                    for model in used_in_models
                }

                # ----------------------------
                # Assembly constraints
                # ----------------------------
                model_constraints = {
                    model: self.assembly_constraints.get(model, [])
                    for model in used_in_models
                }

                bottlenecks.append({
                    "part_id": part_id,
                    "days_of_cover": round(days, 2),
                    "severity": severity,
                    "priority": priority,
                    "root_cause": cause,
                    "used_in_models": used_in_models,
                    "capacity_impact": impacted_models,
                    "assembly_constraints": model_constraints
                })

        return bottlenecks
