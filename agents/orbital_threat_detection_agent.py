class OrbitalThreatDetectionAgent:
    def __init__(self, name="Orbital Threat Detection Agent"):
        self.name = name

    def run(self, sensor_data):
        print(f"[{self.name}] Processing sensor data: {sensor_data}")
        # Placeholder for actual threat detection logic
        detected_threats = {"type": "ICBM", "location": "Region A", "trajectory": "High"} # Example
        print(f"[{self.name}] Detected threats: {detected_threats}")
        return detected_threats
