from napalm import get_network_driver

driver = get_network_driver("eos")

device = driver(
    hostname="172.20.20.11",
    username="admin",
    password="admin",
)

device.open()

print("\n--- Facts ---")
facts = device.get_facts()
print(f"Hostname: {facts['hostname']}")
print(f"Vendor: {facts['vendor']}")
print(f"Model: {facts['model']}")
print(f"OS Version: {facts['os_version']}")
print(f"Uptime: {facts['uptime']}")

print("\n--- Interfaces ---")
interfaces = device.get_interfaces()
for name, data in interfaces.items():
    print(f"{name}: {'up' if data['is_up'] else 'down'} | {data['description']}")

print("\n--- BGP Neighbors ---")
bgp = device.get_bgp_neighbors()
for vrf, vrf_data in bgp.items():
    for neighbor, nbr_data in vrf_data['peers'].items():
        state = "Established" if nbr_data['is_up'] else "Down"
        print(f" {neighbor} AS{nbr_data['remote_as']} - {state}")

device.close()