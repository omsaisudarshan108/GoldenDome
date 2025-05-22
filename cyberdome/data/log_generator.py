import json
import random
import time
import uuid
from datetime import datetime, timedelta

class LogGenerator:
    def __init__(self):
        self.user_ids = ["asmith", "bjones", "cdoe", "dking", "elee"]
        self.source_ips = ["192.168.1.101", "10.0.5.23", "172.16.30.14", "remote_unknown_vpn", "corp_server_alpha"]
        self.dest_ips = ["10.0.0.5 (DB_SERVER)", "10.0.0.10 (APP_SERVER_1)", "8.8.8.8 (Google_DNS)", "partner_api_endpoint"]
        self.resources_accessed = ["/api/data/finances", "/admin/config", "shared_drive/project_x_docs", "critical_asset_db_connection"]
        self.actions = ["login_success", "login_failure", "file_access", "file_upload", "resource_access", "api_call", "unusual_login_time", "privilege_escalation_attempt"]
        self.malware_signatures = ["trojan_variant_xyz_payload", "ransomware_encrypt_command", "c2_beacon_heartbeat"]
        self.normal_payloads = ["standard_api_request_json", "html_get_request_assets", "internal_sync_packet_data"]

    def _generate_timestamp(self, hours_offset=0):
        return (datetime.utcnow() - timedelta(minutes=random.randint(0, 60*hours_offset if hours_offset > 0 else 60))).isoformat() + "Z"

    def generate_network_traffic_log(self, anomaly_type=None):
        log = {
            "event_id": str(uuid.uuid4()),
            "timestamp": self._generate_timestamp(2), # logs from past 2 hours
            "type": "network_traffic",
            "source_ip": random.choice(self.source_ips),
            "destination_ip": random.choice(self.dest_ips),
            "destination_port": random.choice([80, 443, 8080, 22, 3389]),
            "protocol": random.choice(["TCP", "UDP", "ICMP"]),
            "payload_size_bytes": random.randint(64, 1500),
        }
        if anomaly_type == "data_exfiltration":
            log["payload"] = f"sensitive_document_chunk_{random.randint(1,100)}.docx"
            log["destination_ip"] = "suspicious_external_ip_1.2.3.4"
            log["payload_size_bytes"] = random.randint(100000, 500000) # Larger payload
            log["notes"] = "Potential data exfiltration signature"
        elif anomaly_type == "malware_signature":
            log["payload"] = random.choice(self.malware_signatures)
            log["notes"] = "Known malware signature detected in payload"
        elif anomaly_type == "suspicious_pattern": # Generic suspicious
             log["payload"] = "suspicious_pattern_exploit_attempt_sensitive_data" # as used in coordinator test
             log["notes"] = "Generic suspicious pattern"
        else:
            log["payload"] = random.choice(self.normal_payloads)
        return log

    def generate_user_activity_log(self, anomaly_type=None):
        log = {
            "event_id": str(uuid.uuid4()),
            "timestamp": self._generate_timestamp(1), # logs from past 1 hour
            "type": "user_activity",
            "user_id": random.choice(self.user_ids),
            "source_ip": random.choice(self.source_ips),
        }
        if anomaly_type == "unusual_login_time":
            log["action"] = "login_success" # or "login_failure"
            log["timestamp"] = (datetime.utcnow() - timedelta(hours=random.randint(3,6), minutes=random.randint(0,59))).isoformat() + "Z" # Off hours
            log["details"] = "Login detected outside of normal working hours."
            log["notes"] = "Behavioral Anomaly: Unusual login time"
        elif anomaly_type == "privilege_escalation":
            log["action"] = "privilege_escalation_attempt"
            log["target_resource"] = "root_access_admin_panel"
            log["status"] = random.choice(["SUCCESS_ESCALATED", "FAILED_DENIED"])
            log["notes"] = "Behavioral Anomaly: Privilege escalation event"
        elif anomaly_type == "sensitive_data_access":
            log["action"] = "resource_access"
            log["resource_id"] = random.choice(self.resources_accessed)
            if "critical_asset" in log["resource_id"] or "finances" in log["resource_id"]:
                 log["notes"] = "Behavioral Anomaly: Access to sensitive data resource"
            log["status"] = random.choice(["granted", "denied_policy"])
        else:
            log["action"] = random.choice(self.actions)
            log["resource_id"] = random.choice(self.resources_accessed) if "access" in log["action"] or "upload" in log["action"] else None
            log["status"] = random.choice(["success", "failure", "pending"]) if "login" in log["action"] else "completed"
        return log

    def generate_mock_logs(self, num_network_logs=10, num_user_logs=10):
        logs = []
        # Generate some normal logs
        for _ in range(num_network_logs - 2): # Save space for anomalies
            logs.append(self.generate_network_traffic_log())
        for _ in range(num_user_logs - 2): # Save space for anomalies
            logs.append(self.generate_user_activity_log())

        # Add specific anomalies for testing
        logs.append(self.generate_network_traffic_log(anomaly_type="malware_signature"))
        logs.append(self.generate_network_traffic_log(anomaly_type="data_exfiltration"))
        logs.append(self.generate_user_activity_log(anomaly_type="unusual_login_time"))
        logs.append(self.generate_user_activity_log(anomaly_type="privilege_escalation"))
        logs.append(self.generate_user_activity_log(anomaly_type="sensitive_data_access"))
        
        # Add one log that matches the coordinator test data for "suspicious_pattern"
        logs.append(self.generate_network_traffic_log(anomaly_type="suspicious_pattern"))


        random.shuffle(logs)
        return logs

    def get_separate_logs(self, num_total_logs=20):
        all_logs = self.generate_mock_logs(num_network_logs=num_total_logs//2, num_user_logs=num_total_logs//2)
        network_traffic_data = [log for log in all_logs if log["type"] == "network_traffic"]
        user_behavior_data = [log for log in all_logs if log["type"] == "user_activity"]
        return network_traffic_data, user_behavior_data


if __name__ == "__main__":
    generator = LogGenerator()

    print("--- Generating Sample Network Traffic Logs ---")
    network_logs, user_logs = generator.get_separate_logs(num_total_logs=10) # Generate 5 of each base, plus anomalies
    
    print(f"Generated {len(network_logs)} network logs:")
    for i, log in enumerate(network_logs[:3]): # Print first 3
        print(json.dumps(log, indent=2))
        if i == 2 and len(network_logs) > 3: print("...")


    print("\n--- Generating Sample User Activity Logs ---")
    print(f"Generated {len(user_logs)} user logs:")
    for i, log in enumerate(user_logs[:3]): # Print first 3
        print(json.dumps(log, indent=2))
        if i == 2 and len(user_logs) > 3: print("...")

    # Example of saving to a file (optional)
    # with open("cyberdome/data/mock_combined_logs.json", "w") as f:
    #     json.dump(network_logs + user_logs, f, indent=2)
    # print("\nSaved mock_combined_logs.json to cyberdome/data/ directory")
