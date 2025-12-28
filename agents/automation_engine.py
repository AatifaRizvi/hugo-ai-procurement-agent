# agents/automation_engine.py

class AutomationEngine:
    def __init__(self, snapshot):
        self.snapshot = snapshot

    def run_automation(self):
        alerts = []
        for part in self.snapshot:
            if part.get("days_of_cover", 0) < 5:
                alerts.append(
                    f"ALERT: {part['part_id']} running low, only {part['days_of_cover']} days left!"
                )
        return alerts
