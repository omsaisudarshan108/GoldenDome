from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List, Optional
import operator

from cyberdome.agents import (
    ReconAgent,
    ExploitClassifierAgent,
    ContainmentAgent,
    IncidentNarratorAgent,
    HumanReviewBoardCrew,
    ZeroTrustAgent # Add this
)

# Define the state for our CyberDome graph
class CyberDomeState(TypedDict):
    raw_network_traffic_data: Optional[list]
    raw_user_behavior_data: Optional[list]
    detected_anomalies: Annotated[Optional[List[dict]], operator.add]
    classified_exploits: Annotated[Optional[List[dict]], operator.add]
    zero_trust_evaluations: Optional[List[dict]] # Add this
    # Flag to determine if human review is needed for a specific action/exploit
    human_review_needed_for_critical_action: bool 
    # Stores the details of the action requiring review
    action_requiring_review: Optional[dict]
    human_review_decision: Optional[dict]
    containment_actions: Annotated[Optional[List[dict]], operator.add]
    incident_summary: Optional[str]
    # Control flow:
    current_critical_exploit_index: Optional[int] # If we iterate through critical exploits for review
    processed_exploit_ids: List[str] # To avoid reprocessing
    # Add other state fields here if needed during evolution

class AISocCoordinationNode:
    def __init__(self):
        self.recon_agent = ReconAgent()
        self.exploit_classifier_agent = ExploitClassifierAgent()
        self.containment_agent = ContainmentAgent()
        self.narrator_agent = IncidentNarratorAgent()
        self.human_review_board = HumanReviewBoardCrew()
        self.zero_trust_agent = ZeroTrustAgent() # Add this

        self.workflow = StateGraph(CyberDomeState)
        self._build_graph()
        self.app = self.workflow.compile()

    # Agent Nodes
    def _run_reconnaissance(self, state: CyberDomeState):
        print("\n--- Node: Reconnaissance ---")
        network_data = state.get("raw_network_traffic_data", [])
        user_data = state.get("raw_user_behavior_data", [])
        anomalies = self.recon_agent.run(network_traffic_data=network_data, user_behavior_data=user_data)
        return {"detected_anomalies": anomalies, "processed_exploit_ids": []}

    def _run_classification(self, state: CyberDomeState):
        print("\n--- Node: Exploit Classification ---")
        anomalies = state.get("detected_anomalies")
        if not anomalies:
            print("No anomalies to classify.")
            return {"classified_exploits": []}
        classified = self.exploit_classifier_agent.run(anomalies)
        return {"classified_exploits": classified}

    def _run_containment(self, state: CyberDomeState):
        print("\n--- Node: Containment ---")
        exploits = state.get("classified_exploits")
        if not exploits:
            print("No classified exploits for containment.")
            return {"containment_actions": []}
        
        # Filter exploits: only act on approved or non-critical ones not needing review
        exploits_for_containment = []
        human_decision_map = state.get("human_review_decision", {})
        
        for exploit in exploits:
            exploit_id = exploit.get("original_anomaly", {}).get("log", {}).get("event_id", str(exploit)) # simplified ID
            
            # If this exploit was reviewed, check its decision
            if exploit_id in human_decision_map:
                if human_decision_map[exploit_id].get("decision") == "APPROVE":
                    exploits_for_containment.append(exploit)
            else: # If not reviewed, assume it didn't require review based on earlier logic
                exploits_for_containment.append(exploit)
        
        if not exploits_for_containment:
            print("No exploits approved or eligible for containment after review.")
            return {"containment_actions": []}

        actions = self.containment_agent.run(exploits_for_containment)
        return {"containment_actions": actions}

    def _run_narration(self, state: CyberDomeState):
        print("\n--- Node: Incident Narration ---")
        summary = self.narrator_agent.run(state) # Narrator can access the whole state
        return {"incident_summary": summary}

    # Human Review Nodes & Logic
    def _prepare_for_human_review(self, state: CyberDomeState):
        print("\n--- Node: Prepare for Human Review ---")
        exploits = state.get("classified_exploits", [])
        # In a more complex system, we might iterate. Here, we focus on the first critical one.
        # Or, aggregate critical actions. For simplicity, let's assume one "main" action for review if needed.
        
        critical_action_details = None
        requires_policy_level_review = False

        # Identify if any exploit requires review (e.g., critical severity AND specific patterns)
        # This is a simplified check. A real system might have more complex criteria.
        for exploit in exploits:
            exploit_id = exploit.get("original_anomaly", {}).get("log", {}).get("event_id", str(exploit))
            processed_ids = state.get("processed_exploit_ids", [])
            if exploit_id in processed_ids: # Skip if already processed (e.g. reviewed)
                continue

            if exploit.get("severity") == "Critical" or \
               (exploit.get("severity") == "High" and "sensitive_data" in str(exploit.get("original_anomaly"))): # Example criteria
                
                critical_action_details = {
                    "action_summary": f"Contain suspected critical exploit: {exploit.get('signature')}",
                    "details": f"Exploit: {exploit.get('signature')}, Anomaly: {exploit.get('original_anomaly')}",
                    "severity": exploit.get('severity'),
                    "exploit_id": exploit_id # Important for mapping decision back
                }
                # Example: certain actions always require top-level review
                if "critical_asset_compromise" in exploit.get("signature", "").lower(): 
                    requires_policy_level_review = True
                break # Process one critical action review at a time for this example
        
        if critical_action_details:
            print(f"Critical action identified requiring review: {critical_action_details['action_summary']}")
            return {
                "human_review_needed_for_critical_action": True, 
                "action_requiring_review": critical_action_details,
                "current_critical_exploit_index": 0 # Reset/set index
            }
        else:
            print("No critical actions requiring human review at this time.")
            return {
                "human_review_needed_for_critical_action": False,
                "action_requiring_review": None
            }

    def _request_human_review(self, state: CyberDomeState):
        print("\n--- Node: Request Human Review ---")
        action_to_review = state.get("action_requiring_review")
        if not action_to_review:
            # Should not happen if logic is correct
            return {"human_review_decision": {"final_decision_for_graph": "SKIP"}} 

        # Determine if policy override level is needed (e.g. based on action_to_review details)
        policy_level = "critical_asset" in action_to_review.get('details','').lower() # Simplified
        
        review_result = self.human_review_board.review_proposed_action(
            action_to_review, 
            requires_policy_override=policy_level
        )
        
        exploit_id_reviewed = action_to_review["exploit_id"]
        current_decisions = state.get("human_review_decision", {})
        current_decisions[exploit_id_reviewed] = review_result # Store decision mapped to exploit_id

        processed_ids = state.get("processed_exploit_ids", [])
        processed_ids.append(exploit_id_reviewed)

        return {"human_review_decision": current_decisions, "processed_exploit_ids": processed_ids}


    # Conditional Edges
    def _should_request_human_review(self, state: CyberDomeState):
        print("\n--- Conditional Edge: Should Request Human Review? ---")
        if state.get("human_review_needed_for_critical_action") and state.get("action_requiring_review"):
            exploit_id = state.get("action_requiring_review").get("exploit_id")
            # Check if this specific exploit has already been reviewed (e.g., in a loop)
            if exploit_id not in state.get("human_review_decision", {}): # Check against the map of decisions
                print("Yes, critical action found, proceeding to human review.")
                return "request_human_review" 
            else: # If it was already reviewed (e.g. due to graph re-entry with same action_requiring_review)
                print(f"Exploit {exploit_id} already reviewed. Proceeding without new review.")


        print("No (further) human review needed for critical actions. Proceeding to containment or next step.")
        return "run_containment" # Default to containment if no review needed or after review

    def _after_human_review_router(self, state: CyberDomeState):
        print("\n--- Conditional Edge: After Human Review Router ---")
        # This router can decide if more reviews are needed or if we proceed
        
        # Re-check if another critical action needs review by attempting to prepare one
        # This relies on _prepare_for_human_review to find the *next* unreviewed critical exploit.
        exploits = state.get("classified_exploits", [])
        processed_ids = state.get("processed_exploit_ids", [])
        
        next_action_to_review = None
        for exploit in exploits:
            exploit_id = exploit.get("original_anomaly", {}).get("log", {}).get("event_id", str(exploit))
            if exploit_id in processed_ids: # Skip if already processed/reviewed
                continue

            if exploit.get("severity") == "Critical" or \
               (exploit.get("severity") == "High" and "sensitive_data" in str(exploit.get("original_anomaly"))):
                # Found another unreviewed critical exploit
                next_action_to_review = exploit 
                break
        
        if next_action_to_review:
            print("Another critical action found. Looping back to prepare for human review.")
            return "prepare_for_human_review" # Loop back to prepare and then request review for the new one
        else:
            print("All critical actions reviewed or no more critical actions. Proceeding to containment.")
            return "run_containment"


    def _build_graph(self):
        self.workflow.add_node("reconnaissance", self._run_reconnaissance)
        self.workflow.add_node("classification", self._run_classification)
        self.workflow.add_node("prepare_for_human_review", self._prepare_for_human_review)
        self.workflow.add_node("request_human_review", self._request_human_review)
        self.workflow.add_node("containment", self._run_containment)
        self.workflow.add_node("narration", self._run_narration)
        self.workflow.add_node("zero_trust_check", self._run_zero_trust_check) # Add this

        self.workflow.set_entry_point("reconnaissance")
        self.workflow.add_edge("reconnaissance", "classification")
        
        self.workflow.add_edge("classification", "zero_trust_check") # Modified Edge
        self.workflow.add_edge("zero_trust_check", "prepare_for_human_review") # New Edge

        self.workflow.add_conditional_edges(
            "prepare_for_human_review",
            self._should_request_human_review,
            {
                "request_human_review": "request_human_review", # Go to review
                "run_containment": "containment"    # Skip review, go to containment
            }
        )
        
        # After review, decide if more reviews are needed or proceed to containment
        self.workflow.add_conditional_edges(
            "request_human_review",
            self._after_human_review_router,
            {
                "prepare_for_human_review": "prepare_for_human_review", # Loop for more reviews
                "run_containment": "containment" # Done with reviews
            }
        )
        
        self.workflow.add_edge("containment", "narration")
        self.workflow.add_edge("narration", END)

    def run_simulation(self, initial_traffic_data, initial_user_data):
        inputs = {
            "raw_network_traffic_data": initial_traffic_data,
            "raw_user_behavior_data": initial_user_data,
            "human_review_decision": {} # Initialize empty map for decisions
        }
        print("\n--- Starting CyberDome AI SOC Simulation ---")
        final_state = self.app.invoke(inputs)
        print("\n--- CyberDome AI SOC Simulation Complete ---")
        print("Final State:")
        # Pretty print important parts of the final state
        print(f"  Detected Anomalies: {len(final_state.get('detected_anomalies', []))}")
        print(f"  Classified Exploits: {len(final_state.get('classified_exploits', []))}")
        print(f"  Containment Actions: {len(final_state.get('containment_actions', []))}")
        if final_state.get('human_review_decision'):
             print(f"  Human Review Decisions: {final_state.get('human_review_decision')}")
        print(f"  Incident Summary:\n{final_state.get('incident_summary', 'Not generated.')}")
        return final_state

if __name__ == '__main__':
    # Example Usage (for testing this module directly)
    coordinator = AISocCoordinationNode()

    # Mock Data
    mock_traffic = [
        {"event_id": "traffic_001", "source_ip": "1.2.3.4", "dest_ip": "10.0.0.5", "port": 443, "payload": "normal_traffic_pattern_1"},
        {"event_id": "traffic_002", "source_ip": "5.6.7.8", "dest_ip": "10.0.0.5", "port": 80, "payload": "suspicious_pattern_exploit_attempt_sensitive_data"},
    ]
    mock_user_logs = [
        {"event_id": "user_001", "user_id": "asmith", "action": "login_success", "timestamp": "2024-07-31T08:00:00Z", "source_ip": "local"},
        {"event_id": "user_002", "user_id": "bjones", "action": "unusual_login_time", "timestamp": "2024-07-31T03:00:00Z", "source_ip": "remote_unknown"},
        {"event_id": "user_003", "user_id": "bjones", "action": "resource_access", "resource_id": "critical_asset_db", "status": "denied_policy", "source_ip": "remote_unknown"}, # Added source_ip for containment
    ]
    
    # To visualize the graph (optional, requires matplotlib and pygraphviz or pydot)
    # try:
    #     from PIL import Image
    #     import io
    #     img_bytes = coordinator.app.get_graph().draw_mermaid_png()
    #     if img_bytes:
    #         # img = Image.open(io.BytesIO(img_bytes))
    #         # img.show() 
    #         with open("cyberdome_soc_graph.png", "wb") as f:
    #             f.write(img_bytes)
    #         print("Saved simulation graph to cyberdome_soc_graph.png")
    # except Exception as e:
    #     print(f"Could not generate graph image: {e}")

    results = coordinator.run_simulation(mock_traffic, mock_user_logs)
    # print(results) # Full state can be very verbose
