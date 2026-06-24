from nornir import InitNornir
from nornir.core.task import Task, Result 
from nornir_netmiko.tasks import netmiko_send_config, netmiko_send_command
from nornir_utils.plugins.functions import print_result 
from nornir.core.filter import F
import sys, os 
#bootstrap so 'from lib..' resolves regardless of launch dir (same as 18)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.gitops import git_commit

nr = InitNornir(config_file="nornir_config.yaml")

def push_vtep_loopback(task:Task) ->Result:
    #read THIS host's value from inventory - leaf1 gets .1, leaf2 gets .2.
    #this is the whole point of option (a): the data is per host, not hardcoded.
    vtep_ip = task.host["vtep_ip"]

    #pre-check: is Loopback1 already configured with this address?
    #'show run interfaces Loopback1' needs priviledged mode -> enable=True

    current = task.run(
        task=netmiko_send_command,
        command_string="show running-config interface Loopback1",
        enable=True,
    )
    if vtep_ip in current.result:
        return Result(
            host=task.host,
            result=f"{task.host.name}: Loopback1 already {vtep_ip} - skip", 
            changed=False
        )
    # build the three config blocks, injecting this host's vtep_ip + its OWN bgp ASN.
    #netmiko_send_config enters config mode and applies to the list in order.
    commands = [
        "interface Loopback1",
        "description VTEP_SOURCE", 
        f"ip address {vtep_ip}",
        "router ospf 1",
        f"network {vtep_ip} area 0.0.0.0"
        #NOTE: bgp 'network' wants the prefix WITHOUT the /32 mask split out;
        #EOS accepts 'network 10.0.2.1/32' fine, so pass vtep_ip as-is.
        f"router bgp {task.host['bgp']['local_as']}",
        f"      network {vtep_ip}",
    ]
    task.run(task=netmiko_send_config, config_commands=commands)
    task.run(task=netmiko_send_command, command_string="write memory")

    return Result(host=task.host,
                  result=f"{task.host.name}: Loopback1 {vtep_ip} pushed + saved",
                  changed = True)

# only the leaves are VTEPs - spines are NOT. filter on the 'leaf' group.
leaves = nr.filter(F(groups__contains="leaf"))
result = leaves.run(task=push_vtep_loopback)
print_result(result)

git_commit(
    ["scripts/19_vtep_loopback.py"],
    "A1: push VTEP Loopback1 on leaves (10.0.2.0/24)"
)