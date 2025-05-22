class ContainmentAgent:
    def __init__(self, name="Containment Agent"):
        self.name = name

    def isolate_endpoint(self, endpoint_id, reason):
        # Placeholder for API calls to Crowdstrike, SentinelOne, etc.
        print(f"[{self.name}] SIMULATING: Isolating endpoint '{endpoint_id}' due to: {reason}.")
        print(f"[{self.name}] SIMULATING: API call to security tool (e.g., Crowdstrike) would happen here.")
        return {"endpoint_id": endpoint_id, "status": "isolated_simulated", "reason": reason}

    def run(self, classified_exploits_data):
        print(f"\n[{self.name}] Starting containment actions based on {len(classified_exploits_data)} classified exploits...")
        containment_actions = []
        for exploit in classified_exploits_data:
            if exploit.get("severity") in ["High", "Critical"] or exploit.get("kill_chain_interrupted_flag"):
                # Determine endpoint from anomaly data (simplified)
                endpoint_to_isolate = exploit.get("original_anomaly", {}).get("log", {}).get("source_ip", "unknown_endpoint")
                if endpoint_to_isolate == "unknown_endpoint":
                     endpoint_to_isolate = exploit.get("original_anomaly", {}).get("log", {}).get("user_id", "unknown_user_endpoint")

                print(f"[{self.name}] High severity or kill chain exploit detected: {exploit.get('signature')}. Triggering containment for endpoint: {endpoint_to_isolate}")
                action_result = self.isolate_endpoint(
                    endpoint_id=endpoint_to_isolate,
                    reason=f"Classified exploit: {exploit.get('signature')}, Severity: {exploit.get('severity')}"
                )
                containment_actions.append(action_result)
        if not containment_actions:
            print(f"[{self.name}] No high severity exploits requiring immediate containment.")
        print(f"[{self.name}] Containment actions complete. Actions taken: {len(containment_actions)}")
        return containment_actions
