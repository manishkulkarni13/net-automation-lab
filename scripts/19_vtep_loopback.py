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

def push_vtep_loopback(task: Task) -> Result:
    vtep_ip = task.host["vtep_ip"]
    asn = task.host["bgp"]["local_as"]          # pull once, reuse below

    # pre-check: grab the FULL running-config and verify ALL THREE pieces are present.
    # checking only the loopback can't tell "fully done" from "half done".
    current = task.run(
        task=netmiko_send_command,
        command_string="show running-config",
        enable=True,
    )
    cfg = current.result

    # the three things this script is responsible for:
    has_loopback = f"ip address {vtep_ip}" in cfg
    has_ospf     = f"network {vtep_ip} area" in cfg
    has_bgp      = f"network {vtep_ip}" in cfg and f"router bgp {asn}" in cfg

    if has_loopback and has_ospf and has_bgp:
        return Result(
            host=task.host,
            result=f"{task.host.name}: VTEP {vtep_ip} fully configured — skip",
            changed=False,
        )

    # not all present -> (re)push. every line is idempotent, so re-sending
    # the parts that already exist is a harmless no-op.
    commands = [
        "interface Loopback1",
        "description VTEP_SOURCE",
        f"ip address {vtep_ip}",
        "router ospf 1",
        f"network {vtep_ip} area 0.0.0.0",
        f"router bgp {asn}",
        f"network {vtep_ip}",
    ]
    task.run(task=netmiko_send_config, config_commands=commands)
    task.run(task=netmiko_send_command, command_string="write memory")

    return Result(
        host=task.host,
        result=f"{task.host.name}: VTEP {vtep_ip} pushed + saved",
        changed=True,
    )

# only the leaves are VTEPs - spines are NOT. filter on the 'leaf' group.
leaves = nr.filter(F(groups__contains="leaf"))
result = leaves.run(task=push_vtep_loopback)
print_result(result)

git_commit(
    ["scripts/19_vtep_loopback.py"],
    "A1: push VTEP Loopback1 on leaves (10.0.2.0/24)"
)