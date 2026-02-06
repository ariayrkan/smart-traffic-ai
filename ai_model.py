class TrafficAI:
    def make_decision(self, data):
        if data["emergency_vehicle"]:
            return "GREEN_ALL"
        if data["vehicle_count"] > 10:
            return "EXTEND_GREEN"
        return "NORMAL_CYCLE"
