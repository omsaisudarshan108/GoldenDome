from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator

from agents import (
    OrbitalThreatDetectionAgent,
    InterceptorAssignmentAgent,
    StrategicCommandAgent,
    HumanOversightCrew
)

# Define the state for our graph
class SimulationState(TypedDict):
    raw_sensor_data: any
    detected_threats: Annotated[dict, operator.add]
    interceptor_plan: Annotated[dict, operator.add]
    coordinated_action: Annotated[dict, operator.add]
    human_review_needed: bool
    human_decision: dict
    final_outcome: str # To store the final result of the chain

class Orchestrator:
    def __init__(self):
        self.orbital_agent = OrbitalThreatDetectionAgent()
        self.interceptor_agent = InterceptorAssignmentAgent()
        self.strategic_agent = StrategicCommandAgent()
        self.oversight_crew = HumanOversightCrew()

        self.workflow = StateGraph(SimulationState)
        self._build_graph()
        self.app = self.workflow.compile()

    def _detect_threats(self, state: SimulationState):
        print("\n--- Node: Detect Threats ---")
        raw_data = state.get("raw_sensor_data")
        detected_threats = self.orbital_agent.run(raw_data)
        return {"detected_threats": detected_threats, "human_review_needed": True} # Assume review is always needed for now

    def _assign_interceptors(self, state: SimulationState):
        print("\n--- Node: Assign Interceptors ---")
        threats = state.get("detected_threats")
        interceptor_plan = self.interceptor_agent.run(threats)
        return {"interceptor_plan": interceptor_plan}

    def _coordinate_strategy(self, state: SimulationState):
        print("\n--- Node: Coordinate Strategy ---")
        plan = state.get("interceptor_plan")
        coordinated_action = self.strategic_agent.run(plan)
        return {"coordinated_action": coordinated_action}

    def _request_human_review(self, state: SimulationState):
        print("\n--- Node: Request Human Review ---")
        action_to_review = state.get("coordinated_action") # Or could be interceptor_plan
        # For now, we'll use a simplified version of the interceptor plan for review
        review_result = self.oversight_crew.review_action(action_to_review) 
        return {"human_decision": review_result}

    def _decide_next_step(self, state: SimulationState):
        print("\n--- Node: Decide Next Step ---")
        if state.get("human_review_needed"):
            decision = state.get("human_decision", {}).get("decision")
            print(f"Human decision: {decision}")
            if decision == "APPROVE":
                return "execute_action" # Approved, proceed
            else:
                return "end_simulation_rejected" # Rejected, end
        return "end_simulation_no_review" # Should not happen with current logic

    def _execute_action(self, state: SimulationState):
        print("\n--- Node: Execute Action ---")
        print(f"Action approved: {state.get('human_decision')}")
        print(f"Executing coordinated action: {state.get('coordinated_action')}")
        # In a real system, this would trigger actual interceptor launch, etc.
        return {"final_outcome": "Action Executed as per Human Approval"}
    
    def _end_simulation_rejected(self, state: SimulationState):
        print("\n--- Node: End Simulation (Rejected) ---")
        print(f"Action rejected by human oversight: {state.get('human_decision')}")
        return {"final_outcome": "Action Rejected by Human Oversight"}

    def _end_simulation_no_review(self, state: SimulationState):
        print("\n--- Node: End Simulation (No Review) ---")
        print(f"Simulation ended without human review (should not happen with current setup).")
        return {"final_outcome": "Simulation Ended - No Review Path"}


    def _build_graph(self):
        self.workflow.add_node("detect_threats", self._detect_threats)
        self.workflow.add_node("assign_interceptors", self._assign_interceptors)
        self.workflow.add_node("coordinate_strategy", self._coordinate_strategy)
        self.workflow.add_node("request_human_review", self._request_human_review)
        self.workflow.add_node("execute_action", self._execute_action)
        self.workflow.add_node("end_simulation_rejected", self._end_simulation_rejected)
        self.workflow.add_node("end_simulation_no_review", self._end_simulation_no_review)


        self.workflow.set_entry_point("detect_threats")
        self.workflow.add_edge("detect_threats", "assign_interceptors")
        self.workflow.add_edge("assign_interceptors", "coordinate_strategy")
        self.workflow.add_edge("coordinate_strategy", "request_human_review")
        
        self.workflow.add_conditional_edges(
            "request_human_review",
            self._decide_next_step,
            {
                "execute_action": "execute_action",
                "end_simulation_rejected": "end_simulation_rejected",
                "end_simulation_no_review": "end_simulation_no_review" # Fallback
            }
        )
        self.workflow.add_edge("execute_action", END)
        self.workflow.add_edge("end_simulation_rejected", END)
        self.workflow.add_edge("end_simulation_no_review", END)


    def run_simulation(self, initial_sensor_data):
        inputs = {"raw_sensor_data": initial_sensor_data}
        print("\n--- Starting Simulation Run ---")
        final_state = self.app.invoke(inputs)
        print("\n--- Simulation Run Complete ---")
        print(f"Final State: {final_state}")
        return final_state

if __name__ == '__main__':
    # Example Usage (for testing this module directly)
    orchestrator = Orchestrator()
    mock_data = {"source": "Satellite Z", "type": "Hypersonic Missile", "timestamp": "2024-07-30T10:00:00Z"}
    
    # To visualize the graph (optional, requires matplotlib and pygraphviz or pydot)
    # try:
    #     from PIL import Image
    #     import io
    #     img_bytes = orchestrator.app.get_graph().draw_mermaid_png()
    #     if img_bytes:
    #         img = Image.open(io.BytesIO(img_bytes))
    #         img.show() # This will try to open the image with the default viewer
    #         img.save("simulation_graph.png")
    #         print("Saved simulation graph to simulation_graph.png")
    # except Exception as e:
    #     print(f"Could not generate graph image: {e}")

    result = orchestrator.run_simulation(mock_data)
    print(f"\nSimulation Final Outcome: {result.get('final_outcome')}")
