import os
from pygnmi.client import gNMIclient
from pprint import pprint 

#connect to spine1
with gNMIclient(
    target=("172.20.20.11", 6030),
    username=os.environ["cEOS_USER"],
    password=os.environ["cEOS_PASS"],
    insecure=True
) as gc:
    # Get hostname
    result = gc.get(path=["system/config/hostname"])
    pprint("--- Hostname ---")
    pprint(result)

    # Get interface state 
    result = gc.get(path=["interfaces/interface[name=Ethernet1]/state"])
    pprint("--- Ethernet1 State ---")
    for notification in result["notification"]:
        for update in notification["update"]:
            pprint(f"{update['path']}: {update['val']}")

    #Extract specifi counters cleanly
    result = gc.get(path=["interfaces/interface[name=Ethernet1]/state/counters"])
    pprint("--- Ethernet1 Counters ---")
    for notification in result["notification"]:
        for update in notification["update"]:
            counters = update["val"]
            pprint(f"In octets : {counters.get('openconfig-interfaces:in-octets', 'N/A')}")
            pprint(f"Out octets: {counters.get('openconfig-interfaces:out-octets', 'N/A')}")
            pprint(f"In errors : {counters.get('openconfig-interfaces:in-errors', 'N/A')}")
            pprint(f"Out errors : {counters.get('openconfig-interfaces:out-errors', 'N/A')}")
            pprint(f"Carrier transitions: {counters.get('openconfig-interfaces:carrier-transitions', 'N/A')}")