import os
import requests
import json
import urllib3
from datetime import datetime

urllib3.disable_warnings()

DEVICES = {
    "spine1": "172.20.20.11",
    "spine2": "172.20.20.12",
    "leaf1": "172.20.20.13",
    "leaf2": "172.20.20.14"
}

def eapi_call(host, commands):
    payload = {
        "jsonrpc": "2.0",
        "method": "runCmds",
        "params": {"version":1, "cmds":commands, "format":"json"},
        "id": 1
    }

    try:
        response = requests.post(
            f"https://{host}/command-api",
            json=payload,
            auth=(os.environ["cEOS_USER"], os.environ["cEOS_PASS"]),
            verify=False,
            timeout=10
        )
        return response.json()["result"]
    except Exception as e:
        return None

report = {
    "timestamp": datetime.now().isoformat(),
    "healthy":[],
    "degraded":[],
    "unreachable":[]
}

for hostname, ip  in DEVICES.items():
    result = eapi_call(ip, ["show ip bgp summary"])

    if result is None:
        report["unreachable"].append(hostname)
        print(f"UNREACHABLE: {hostname}")
        continue

    peers = result[0]["vrfs"]["default"]["peers"]
    down=[]

    for peer_ip, data in peers.items():
        if data["peerState"] != "Established":
            down.append({
                "peer": peer_ip, 
                "asn": data["asn"],
                "state": data["peerState"]
            })

    if down:
        report["degraded"].append({
            "device": hostname,
            "down_peers": down
        })
        print(f"DEGRADED: {hostname} - {len(down)} BGP peer(s) down")
        for d in down:
            print(f" {d['peer']} AS{d['asn']} - {d['state']}")
    else:
        report["healthy"].append(hostname)
        print(f"HEALTHY: {hostname} - all BGP peers Established")

print(f"\nSummary: {len(report['healthy'])} healthy |"
      f"{len(report['degraded'])} degraded |"
      f"{len(report['unreachable'])} unreachable")
    
with open(f"outputs/bgp_health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
    json.dump(report, f, indent=2)

      