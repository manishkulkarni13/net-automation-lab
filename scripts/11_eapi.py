import os
import requests
import json
import urllib3

urllib3.disable_warnings()

def eapi_call(host, commands):
    payload = {
        "jsonrpc": "2.0",
        "method": "runCmds",
        "params": {
            "version": 1,
            "cmds": commands,
            "format": "json"
        },
        "id": 1
    }
    response = requests.post(
        f"https://{host}/command-api",
        json=payload,
        auth=(os.environ["cEOS_USER"], os.environ["cEOS_PASS"]),
        verify=False
    )
    return response.json()["result"]

# Query all 4 devices
devices = ["172.20.20.11", "172.20.20.12", "172.20.20.13", "172.20.20.14"]

for device in devices:
    result = eapi_call(device, ["show ip bgp summary"])
    bgp = result[0]
    print(f"\n{device}:")
    for peer, data in bgp["vrfs"]["default"]["peers"].items():
        state = data["peerState"]
        asn = data["asn"]
        print(f"  {peer} AS{asn} — {state}")