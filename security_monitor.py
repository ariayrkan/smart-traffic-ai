class SecurityMonitor:
    def detect_attack(self, data):
        if data["vehicle_count"] > 100:
            return True
        return False
