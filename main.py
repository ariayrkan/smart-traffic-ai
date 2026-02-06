from sensors import SensorInput
from ai_model import TrafficAI
from security_monitor import SecurityMonitor
from controller import TrafficController

def main():
    sensors = SensorInput()
    ai = TrafficAI()
    security = SecurityMonitor()
    controller = TrafficController()

    sensor_data = sensors.read_data()

    if security.detect_attack(sensor_data):
        controller.safe_mode()
    else:
        decision = ai.make_decision(sensor_data)
        controller.apply_decision(decision)

if __name__ == "__main__":
    main()
