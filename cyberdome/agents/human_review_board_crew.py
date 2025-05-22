from crewai import Agent, Task, Crew, Process

class HumanReviewBoardCrew:
    def __init__(self):
        # Define the Policy Override Agent
        self.policy_override_agent = Agent(
            role='Policy Override Agent (CISO/Compliance Designate)',
            goal=(
                "Review critical cybersecurity actions against business policy, ethical guidelines, and compliance regulations. "
                "Provide override decisions or approvals based on a holistic view of risk and business impact."
            ),
            backstory=(
                "A senior executive or designated compliance officer with deep understanding of the organization's risk appetite, "
                "legal obligations, and strategic goals. Acts as a crucial checkpoint for automated decisions that might have "
                "significant operational or business consequences."
            ),
            verbose=True,
            allow_delegation=False, # This agent makes the final call on policy matters
            # llm=... # Placeholder for a specific LLM if needed, otherwise uses default
        )

        # General Reviewer (Could be a SOC manager or similar role)
        self.security_reviewer_agent = Agent(
            role='Security Operations Reviewer',
            goal='Provide a first-pass review of proposed actions, validating technical soundness and immediate operational impact.',
            backstory=(
                "An experienced security operations professional responsible for overseeing real-time cyber defense activities. "
                "Focuses on the technical execution and immediate implications of proposed actions."
            ),
            verbose=True,
            allow_delegation=False,
        )


    def review_proposed_action(self, proposed_action_details, requires_policy_override=False):
        print(f"\n[Human Review Board] Received action for review: {proposed_action_details}")
        
        review_agent = self.security_reviewer_agent
        if requires_policy_override:
            print("[Human Review Board] This action requires policy override level review.")
            review_agent = self.policy_override_agent
        
        # Define the task for the selected agent
        review_task = Task(
            description=(
                f"Review the following proposed cybersecurity action: '{proposed_action_details.get('action_summary', 'N/A')}'. "
                f"Details: {proposed_action_details.get('details', 'N/A')}. "
                f"Assessed Severity: {proposed_action_details.get('severity', 'N/A')}. "
                "Consider potential impact, accuracy of assessment, and alignment with security objectives. "
                "If you are the Policy Override Agent, also consider business policy, ethics, and compliance. "
                "Respond with 'APPROVE' or 'REJECT' and a concise justification."
            ),
            agent=review_agent,
            expected_output="A decision ('APPROVE' or 'REJECT') and a justification string."
        )

        # For this simulation, we'll directly determine the outcome
        # without kicking off a full CrewAI process with an LLM.
        print(f"\n[Human Review Board] Simulating review by {review_agent.role}...")
        
        # Simulated decision logic (can be expanded)
        decision = "APPROVE" # Default to approve for simulation
        justification = f"Simulated approval by {review_agent.role}. Action appears warranted based on available data."

        if requires_policy_override:
            justification = f"Simulated policy override approval by {review_agent.role}. Action authorized considering broader business context."

        # Example of a more nuanced simulated decision:
        # if "critical_asset" in proposed_action_details.get('details', '').lower() and requires_policy_override:
        #     decision = "REJECT" # Or require further input
        #     justification = f"Simulated REJECTION by {review_agent.role} due to critical asset involvement. Requires executive sign-off."

        print(f"[Human Review Board] Decision: {decision}, Justification: {justification}")
        
        return {
            "decision": decision, 
            "justification": justification, 
            "reviewer_role": review_agent.role,
            "policy_agent_role": self.policy_override_agent.role if requires_policy_override else "N/A"
        }

if __name__ == '__main__':
    board = HumanReviewBoardCrew()
    
    action1 = {
        "action_summary": "Isolate compromised endpoint", 
        "details": "Endpoint IP: 192.168.1.101, User: bsimpson, Exploit: CVE-2023-12345",
        "severity": "High"
    }
    print("\n--- Test Case 1: Standard Security Review ---")
    result1 = board.review_proposed_action(action1, requires_policy_override=False)
    print(f"Review Result: {result1}")

    action2 = {
        "action_summary": "Block traffic from critical partner IP range", 
        "details": "IP Range: 10.20.30.0/24, Reason: Suspected data exfiltration linked to partner network",
        "severity": "Critical"
    }
    print("\n--- Test Case 2: Policy Override Review ---")
    result2 = board.review_proposed_action(action2, requires_policy_override=True)
    print(f"Review Result: {result2}")
