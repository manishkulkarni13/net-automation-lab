import os
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

device = {
    "device_type": "arista_eos",
    "host": "172.20.20.11",
    "username": os.environ["cEOS_USER"],
    "password": os.environ["cEOS_PASS"],
    "secret":os.environ["cEOS_PASS"]
}

try:
    with ConnectHandler(**device) as conn:
        conn.enable()
        print(f"Connected to {conn.find_prompt()}")
        output = conn.send_command("show version")
        print(output)
        config = [
            "interface Loopback100",
            "description MANAGED_BY_AUTOMATION",
            "ip address 10.100.0.1 255.255.255.255",
        ]
        result = conn.send_config_set(config)
        print(result)

        verify = conn.send_command("show interface Loopback100")

except NetmikoTimeoutException:
    print("ERROR: Device unreachable")
except NetmikoAuthenticationException:
    print("Error: Bad Credentials")