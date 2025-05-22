import json
import random
import time
import uuid

class SensorDataGenerator:
    def __init__(self):
        self.threat_types = {
            "ICBM": {
                "speed_range": (7, 8), # km/s
                "altitude_range": (1000, 1200), # km
                "signatures": ["High thermal signature", "Ballistic trajectory"],
            },
            "Hypersonic": {
                "speed_range": (5, 25), # Mach
                "altitude_range": (50, 100), # km
                "signatures": ["Maneuverable flight path", "Plasma sheath"],
            },
            "DroneSwarm": {
                "speed_range": (50, 200), # km/h
                "altitude_range": (0.1, 5), # km
                "signatures": ["Multiple small radar cross-sections", "Coordinated movement"],
                "count_range": (5, 50)
            }
        }
        self.regions = ["Region A", "Region B", "Northern Sector", "Coastal Area X", "High Altitude Zone 5"]
        self.sources = ["Satellite Network Alpha", "Radar Array Sentinel", "Space Surveillance System Omega"]

    def _generate_base_threat(self, threat_category):
        config = self.threat_types[threat_category]
        return {
            "id": str(uuid.uuid4()),
            "category": threat_category,
            "source": random.choice(self.sources),
            "timestamp": time.time(),
            "location": {
                "region": random.choice(self.regions),
                "latitude": round(random.uniform(-90, 90), 6),
                "longitude": round(random.uniform(-180, 180), 6),
            },
            "speed": round(random.uniform(*config["speed_range"]), 2),
            "altitude": round(random.uniform(*config["altitude_range"]), 2),
            "signatures": random.sample(config["signatures"], k=random.randint(1, len(config["signatures"]))),
            "confidence": round(random.uniform(0.75, 0.99), 2)
        }

    def generate_icbm_sighting(self):
        threat = self._generate_base_threat("ICBM")
        threat["details"] = {
            "trajectory_type": "Ballistic",
            "estimated_impact_zone": random.choice(self.regions) # Simplified
        }
        return threat

    def generate_hypersonic_sighting(self):
        threat = self._generate_base_threat("Hypersonic")
        threat["details"] = {
            "maneuvering_capability": random.choice([True, False]),
            "current_heading": round(random.uniform(0, 360), 1) # degrees
        }
        return threat

    def generate_drone_swarm_sighting(self):
        threat = self._generate_base_threat("DroneSwarm")
        threat["details"] = {
            "swarm_size": random.randint(*self.threat_types["DroneSwarm"]["count_range"]),
            "primary_axis_of_advance": round(random.uniform(0, 360), 1) # degrees
        }
        return threat

    def generate_random_threat(self):
        threat_category = random.choice(list(self.threat_types.keys()))
        if threat_category == "ICBM":
            return self.generate_icbm_sighting()
        elif threat_category == "Hypersonic":
            return self.generate_hypersonic_sighting()
        elif threat_category == "DroneSwarm":
            return self.generate_drone_swarm_sighting()

    def generate_multiple_threats(self, count=1):
        return [self.generate_random_threat() for _ in range(count)]


if __name__ == "__main__":
    generator = SensorDataGenerator()

    print("--- Generating Single ICBM Sighting ---")
    icbm_data = generator.generate_icbm_sighting()
    print(json.dumps(icbm_data, indent=2))

    print("\n--- Generating Single Hypersonic Sighting ---")
    hypersonic_data = generator.generate_hypersonic_sighting()
    print(json.dumps(hypersonic_data, indent=2))

    print("\n--- Generating Single Drone Swarm Sighting ---")
    drone_swarm_data = generator.generate_drone_swarm_sighting()
    print(json.dumps(drone_swarm_data, indent=2))
    
    print("\n--- Generating Mixed Threat Scenario (3 threats) ---")
    mixed_threats = generator.generate_multiple_threats(3)
    print(json.dumps(mixed_threats, indent=2))

    # Example of saving to a file
    # with open("data/mock_sensor_feed.json", "w") as f:
    #     json.dump(mixed_threats, f, indent=2)
    # print("\nSaved mock_sensor_feed.json to data/ directory")
