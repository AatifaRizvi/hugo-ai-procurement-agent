# agents/capacity_engine.py

class CapacityEngine:
    """
    Deterministic build capacity calculation.
    Uses only inventory snapshot and model dependency info.
    """

    def __init__(self, snapshot, model_dependencies):
        self.snapshot = snapshot
        self.model_dependencies = model_dependencies

        # Build quick lookup: part_id -> on_hand
        self.inventory = {
            part["part_id"]: part.get("on_hand", 0)
            for part in snapshot
        }

    def compute_capacity(self):
        """
        Returns build capacity per model.
        """
        capacity_report = {}

        for model_entry in self.model_dependencies:
            model = model_entry["model"]
            parts = model_entry["part_id"]

            # Compute how many units each part allows
            part_limits = []
            for part_id in parts:
                on_hand = self.inventory.get(part_id, 0)
                part_limits.append(on_hand)  # qty per model = 1

            if not part_limits:
                max_units = 0
            else:
                max_units = min(part_limits)

            if max_units == 0:
                status = "blocked"
            elif max_units < 5:
                status = "constrained"
            else:
                status = "ok"

            capacity_report[model] = {
                "max_buildable_units": max_units,
                "capacity_status": status,
                "limiting_parts": [
                    p for p in parts if self.inventory.get(p, 0) == max_units
                ]
            }

        return capacity_report
