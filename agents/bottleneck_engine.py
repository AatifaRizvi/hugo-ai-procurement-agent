# agents/bottleneck_engine.py

class BottleneckEngine:
    """
    Identifies bottleneck parts and explains why they are bottlenecks.
    """

    def __init__(self, snapshot, capacity_report=None):
        self.snapshot = snapshot
        self.capacity_report = capacity_report or {}

    def analyze_bottlenecks(self):
        bottlenecks = []

        for part in self.snapshot:
            days = part.get("days_of_cover", float("inf"))
            on_hand = part.get("on_hand", 0)
            part_id = part.get("part_id")

            if days < 5:
                # Determine severity
                if on_hand == 0:
                    severity = "blocking"
                elif days < 2:
                    severity = "critical"
                else:
                    severity = "warning"

                # Root cause classification
                if part.get("next_po_arrival_days") is None:
                    cause = "no_inbound_supply"
                elif part.get("next_po_arrival_days", 0) > days:
                    cause = "late_replenishment"
                else:
                    cause = "demand_spike"

                bottlenecks.append({
                    "part_id": part_id,
                    "days_of_cover": round(days, 2),
                    "severity": severity,
                    "root_cause": cause,
                    "used_in_models": part.get("used_in_models", [])
                })

        return bottlenecks
