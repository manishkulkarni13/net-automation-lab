from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result 
from nornir.core.filter import F
import time

nr = InitNornir(config_file="nornir_config.yaml")

start = time.time()
result = nr.run (
    task = netmiko_send_command,
    command_string = "show version"
)
print(f"Completed in: {time.time() -start:.2f}s")
print_result(result)

print("\n--- Leaves Only ---")
leaves = nr.filter(F(groups__contains="leaf"))
result2 = leaves.run(
    task = netmiko_send_command, 
    command_string= "show ip interface brief"
)
print_result(result2)