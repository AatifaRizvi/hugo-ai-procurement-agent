# agents/capacity_engine.py

class CapacityEngine:
    def __init__(self, snapshot, model_dependencies, bom_quantities):
        self.snapshot = snapshot
        self.model_dependencies = model_dependencies
        self.bom_quantities = bom_quantities

        self.inventory = {
            part["part_id"]: part.get("on_hand", 0)
            for part in snapshot
        }

    def compute_capacity(self):
        capacity_report = {}

        for model_entry in self.model_dependencies:
            model = model_entry["model"]
            parts = model_entry["part_id"]

            part_limits = {}

            for part_id in parts:
                on_hand = self.inventory.get(part_id, 0)
                qty_required = self.bom_quantities.get(model, {}).get(part_id, 1)

                part_limits[part_id] = on_hand // qty_required

            max_units = min(part_limits.values()) if part_limits else 0

            capacity_report[model] = {
                "max_buildable_units": max_units,
                "limiting_parts": [
                    p for p, v in part_limits.items() if v == max_units
                ],
                "capacity_status": (
                    "blocked" if max_units == 0
                    else "constrained" if max_units < 5
                    else "ok"
                )
            }

        return capacity_report
