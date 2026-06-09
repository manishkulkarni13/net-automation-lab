from ncclient import manager
import xmltodict
import json

conn = manager.connect(
    host="172.20.20.11",
    port=830,
    username="admin",
    password="admin",
    hostkey_verify=False,
    device_params={"name": "default"}
)

config = conn.get_config(source="running")
config_dict = xmltodict.parse(str(config))

# Extract hostname
hostname = config_dict['rpc-reply']['data']['system']['config']['hostname']
print(f"\nHostname: {hostname}")

# Extract BGP neighbors
protocols = config_dict['rpc-reply']['data']['network-instances']['network-instance']['protocols']['protocol']

bgp_protocol = None
for p in protocols:
    if 'bgp' in p:
        bgp_protocol = p
        break

neighbors = bgp_protocol['bgp']['neighbors']['neighbor']
print("\nBGP Neighbors:")
for nbr in neighbors:
    ip = nbr['neighbor-address']
    asn = nbr['config']['peer-as']
    print(f"  {ip} AS{asn}")