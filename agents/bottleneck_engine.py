# agents/bottleneck_engine.py
class BottleneckEngine:
    def __init__(self, snapshot):
        self.snapshot = snapshot

    def find_bottlenecks(self):
        bottlenecks = []
        for part in self.snapshot:
            if part.get("days_of_cover", 0) < 5:
                bottlenecks.append(part["part_id"])
        return bottlenecks
