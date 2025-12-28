# agents/supplier_engine.py
class SupplierEngine:
    def __init__(self, snapshot):
        self.snapshot = snapshot

    def analyze_suppliers(self):
        report = {}
        for part in self.snapshot:
            supplier = part.get("supplier", "Unknown")
            report.setdefault(supplier, {"delayed_parts": [], "price_spikes": []})
            if part.get("lead_time", 0) > 10:
                report[supplier]["delayed_parts"].append(part["part_id"])
            if part.get("price_spike", False):
                report[supplier]["price_spikes"].append(part["part_id"])
        return report
