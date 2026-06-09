from napalm import get_network_driver

driver = get_network_driver("eos")

device = driver (
    hostname = "172.20.20.11",
    username = "admin",
    password = "admin",
)

device.open()

#Load a candidate config change without pushing it

new_config = """
interface Loopback200
    description NAPALM_TEST
    ip address 10.200.0.1/32
"""

device.load_merge_candidate(config=new_config)

#Show the diff - what will change
diff = device.compare_config()
print("\--- Config Diff ---")
print(diff)

# Ask before committing 
confirm = input("\nCommit this change? (yes/no): ")
if confirm.strip().lower() == "yes":
    device.commit_config()
    print("Committed.")
    ## Rollback to previous config
    print("\n--- Rolling back ---")
    device.rollback()
    print("Rollback complete.")
else:
    device.discard_config()
    print("Discarded.")


device.close()