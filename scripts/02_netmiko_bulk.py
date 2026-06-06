from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException
import json
from datetime import datetime

DEVICES = [
    {"hostname":"spine1", "host":"172.20.20.11", "device_type":"arista_eos", "username":"admin", "password":"admin", "secret":"admin"},
    {"hostname":"spine2", "host":"172.20.20.12", "device_type":"arista_eos", "username":"admin", "password":"admin", "secret":"admin"}, 
    {"hostname":"leaf1", "host":"172.20.20.13", "device_type":"arista_eos", "username":"admin", "password":"admin", "secret":"admin"},
    {"hostname":"leaf2", "host":"172.20.20.14", "device_type":"arista_eos", "username":"admin", "password":"admin", "secret":"admin"}   
]

results = {
        "success":[],
        "failed":[]
}

for device in DEVICES:
    hostname = device.pop("hostname")
    try:
        with ConnectHandler(**device) as conn:
            conn.enable()
            output = conn.send_command("show version")
            results["success"].append({"host": hostname})
            print(f"OK {hostname}")
    except (NetmikoTimeoutException, NetmikoAuthenticationException, Exception) as e:
        results["failed"].append({"host":hostname, "error": str(e)})
        print(f"FAIL {hostname}: {e}")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
with open(f"../outputs/build_result_{timestamp}.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nSuccess: {len(results['success'])} | Failed: {len(results['failed'])}")