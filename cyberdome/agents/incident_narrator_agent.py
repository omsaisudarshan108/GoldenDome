class IncidentNarratorAgent:
    def __init__(self, name="Incident Narrator Agent"):
        self.name = name

    def summarize_incident(self, all_data_points):
        # all_data_points could be the final state from LangGraph, containing all collected info
        print(f"\n[{self.name}] Generating incident summary...")
        
        summary = "Incident Report:\n"
        summary += "===============\n"
        
        recon_anomalies = all_data_points.get("detected_anomalies", [])
        classified_exploits = all_data_points.get("classified_exploits", [])
        containment_actions = all_data_points.get("containment_actions", [])
        human_review = all_data_points.get("human_review_decision")

        summary += f"1. Reconnaissance Phase:\n"
        if recon_anomalies:
            summary += f"   - Detected {len(recon_anomalies)} initial anomalies.\n"
            for anomaly in recon_anomalies[:2]: # Show first 2
                summary += f"     - Type: {anomaly.get('type')}, Details: {str(anomaly.get('log', '')[:100])}...\n"
        else:
            summary += "   - No anomalies detected in recon phase.\n"

        summary += f"\n2. Classification Phase:\n"
        if classified_exploits:
            summary += f"   - Classified {len(classified_exploits)} exploits.\n"
            for exploit in classified_exploits[:2]: # Show first 2
                summary += f"     - Signature: {exploit.get('signature')}, Severity: {exploit.get('severity')}\n"
                if exploit.get('kill_chain_interrupted_flag'):
                    summary += f"     - Kill Chain Interruption: Attempted/Flagged\n"
        else:
            summary += "   - No exploits classified.\n"

        if human_review:
            summary += f"\n3. Human Review Board Decision:\n"
            summary += f"   - Decision: {human_review.get('decision')}\n"
            summary += f"   - Justification: {human_review.get('justification')}\n"
            summary += f"   - Policy Override Agent: {human_review.get('policy_agent_role', 'N/A')}\n"


        summary += f"\n4. Containment Phase:\n"
        if containment_actions:
            summary += f"   - Executed {len(containment_actions)} containment actions.\n"
            for action in containment_actions:
                summary += f"     - Endpoint: {action.get('endpoint_id')}, Status: {action.get('status')}\n"
        else:
            summary += "   - No containment actions taken.\n"
        
        summary += "\nEnd of Report.\n"
        
        print(summary)
        return summary

    def run(self, final_state_data):
        return self.summarize_incident(final_state_data)
