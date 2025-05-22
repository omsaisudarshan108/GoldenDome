class ZeroTrustAgent:
    def __init__(self, name="Zero Trust Enforcement Agent"):
        self.name = name
        # Example: Define some basic zero trust rules
        # In a real system, these rules would be more complex and managed externally
        self.rules = {
            "critical_asset_db_connection": {"required_mfa": True, "allowed_roles": ["db_admin", "auditor"]},
            "financial_report_access": {"required_mfa": True, "allowed_departments": ["finance", "executive"]},
            "source_code_repository": {"required_mfa": True, "allowed_users": ["dev_team_lead", "senior_developer"]},
        }

    def verify_access_request(self, user_id, resource_id, user_role=None, user_department=None, mfa_status="not_verified"):
        print(f"\n[{self.name}] Verifying access: User '{user_id}' to Resource '{resource_id}'")
        
        if resource_id not in self.rules:
            print(f"[{self.name}] No specific Zero Trust rule for resource '{resource_id}'. Allowing with standard checks (simulated).")
            # In a real ZT model, default deny might be stricter or other checks would apply
            return {"resource_id": resource_id, "user_id": user_id, "decision": "ALLOW_NO_SPECIFIC_ZT_RULE", "reason": "No specific ZT microsegmentation rule found for this resource."}

        rule = self.rules[resource_id]
        
        # MFA Check
        if rule.get("required_mfa") and mfa_status != "verified":
            print(f"[{self.name}] DENY: MFA not verified for '{resource_id}'. MFA status: {mfa_status}.")
            return {"resource_id": resource_id, "user_id": user_id, "decision": "DENY_MFA_REQUIRED", "reason": "MFA verification failed or missing."}

        # Role Check
        if "allowed_roles" in rule and user_role not in rule["allowed_roles"]:
            print(f"[{self.name}] DENY: User role '{user_role}' not authorized for '{resource_id}'. Allowed roles: {rule['allowed_roles']}.")
            return {"resource_id": resource_id, "user_id": user_id, "decision": "DENY_ROLE_MISMATCH", "reason": f"User role '{user_role}' not in allowed roles."}

        # Department Check
        if "allowed_departments" in rule and user_department not in rule["allowed_departments"]:
            print(f"[{self.name}] DENY: User department '{user_department}' not authorized for '{resource_id}'. Allowed departments: {rule['allowed_departments']}.")
            return {"resource_id": resource_id, "user_id": user_id, "decision": "DENY_DEPARTMENT_MISMATCH", "reason": f"User department '{user_department}' not in allowed departments."}
        
        # User Check (if specific users are listed)
        if "allowed_users" in rule and user_id not in rule["allowed_users"]:
            print(f"[{self.name}] DENY: User '{user_id}' not explicitly authorized for '{resource_id}'. Allowed users: {rule['allowed_users']}.")
            return {"resource_id": resource_id, "user_id": user_id, "decision": "DENY_USER_NOT_LISTED", "reason": f"User '{user_id}' not in allowed user list."}

        print(f"[{self.name}] ALLOW: Access for user '{user_id}' to '{resource_id}' meets Zero Trust criteria.")
        return {"resource_id": resource_id, "user_id": user_id, "decision": "ALLOW_ZT_VERIFIED", "reason": "Zero Trust checks passed."}

    def run(self, access_request_details):
        # access_request_details = {"user_id": "asmith", "resource_id": "critical_asset_db_connection", "user_role": "db_admin", "mfa_status": "verified"}
        user_id = access_request_details.get("user_id")
        resource_id = access_request_details.get("resource_id")
        user_role = access_request_details.get("user_role")
        user_department = access_request_details.get("user_department")
        mfa_status = access_request_details.get("mfa_status", "not_verified")
        
        if not user_id or not resource_id:
            print(f"[{self.name}] Invalid access request details received: {access_request_details}")
            return {"decision": "ERROR_INVALID_INPUT", "reason": "Missing user_id or resource_id."}
            
        return self.verify_access_request(user_id, resource_id, user_role, user_department, mfa_status)

if __name__ == '__main__':
    zt_agent = ZeroTrustAgent()
    
    print("--- Test Case 1: Allowed by Role & MFA ---")
    request1 = {"user_id": "asmith", "resource_id": "critical_asset_db_connection", "user_role": "db_admin", "mfa_status": "verified"}
    print(zt_agent.run(request1))

    print("\n--- Test Case 2: Denied by MFA ---")
    request2 = {"user_id": "bjones", "resource_id": "critical_asset_db_connection", "user_role": "db_admin", "mfa_status": "failed"}
    print(zt_agent.run(request2))

    print("\n--- Test Case 3: Denied by Role ---")
    request3 = {"user_id": "cdoe", "resource_id": "critical_asset_db_connection", "user_role": "developer", "mfa_status": "verified"}
    print(zt_agent.run(request3))
    
    print("\n--- Test Case 4: Allowed, no specific rule ---")
    request4 = {"user_id": "dking", "resource_id": "/api/public/info", "mfa_status": "verified"}
    print(zt_agent.run(request4))
    
    print("\n--- Test Case 5: Allowed by Department & MFA ---")
    request5 = {"user_id": "elee", "resource_id": "financial_report_access", "user_department": "finance", "mfa_status": "verified"}
    print(zt_agent.run(request5))
    
    print("\n--- Test Case 6: Denied by Department ---")
    request6 = {"user_id": "asmith", "resource_id": "financial_report_access", "user_department": "engineering", "mfa_status": "verified"}
    print(zt_agent.run(request6))
