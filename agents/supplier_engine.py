# agents/supplier_engine.py

class SupplierEngine:
    """
    Analyzes supplier risk based on email events and part impact.
    """

    def __init__(self, email_events, bottlenecks=None):
        self.email_events = email_events
        self.bottlenecks = bottlenecks or []

    def analyze_suppliers(self):
        supplier_report = {}

        for event in self.email_events:
            supplier = event.get("source", "Unknown")
            event_type = event.get("event_type")

            supplier_report.setdefault(supplier, {
                "delay_events": 0,
                "price_events": 0,
                "quality_events": 0,
                "risk_level": "low",
                "recommended_actions": []
            })

            if event_type == "delay":
                supplier_report[supplier]["delay_events"] += 1
            elif event_type in ("price_update", "discount"):
                supplier_report[supplier]["price_events"] += 1
            elif event_type == "quality_alert":
                supplier_report[supplier]["quality_events"] += 1

        # Derive risk level and actions
        for supplier, data in supplier_report.items():
            if data["delay_events"] > 0 and data["quality_events"] > 0:
                data["risk_level"] = "high"
                data["recommended_actions"].append("consider_alternate_supplier")
            elif data["delay_events"] > 0:
                data["risk_level"] = "medium"
                data["recommended_actions"].append("request_partial_shipment")
            elif data["price_events"] > 0:
                data["risk_level"] = "medium"
                data["recommended_actions"].append("renegotiate_pricing")

        return supplier_report
