from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config 
from nornir_utils.plugins.functions import print_result
import json
from datetime import datetime

nr = InitNornir(config_file="nornir_config.yaml")

def safe_push_with_validate(task: Task) ->Result:
    #1. Snapshot pre-state
    pre = task.run (
        task = netmiko_send_command, 
        command_string = "show ip interface brief",
        enable=True
    )

    pre_state = pre.result 

    #2. Push config
    task.run(
        task=netmiko_send_config, 
        config_commands=[
            "interface Loopback200",
            "description AUTOMATOIN_ROLLBACK_TEST",
            "ip address 10.200.1.1 255.255.255.255"
        ]
    )

    #3. Validate
    post = task.run (
        task=netmiko_send_command,
        command_string="show interface Loopback200",
        enable=True
    )

    if "line protocol is up" not in post.result:
        #. Rollback
        task.run(
            task=netmiko_send_config,
            config_commands =["no interface Loopback200"]
        )
        return Result(
            host=task.host,
            result="ROLLED BACk - validation failed",
            failed = True
        )
    return Result(host=task.host, result="Success - validated")

result = nr.run(task=safe_push_with_validate)

report = {
    "timestamp": datetime.now().isoformat(),
    "succeeded":[],
    "failed":[]
}

for host, r in result.items():
    if r.failed:
        report["failed"].append({"host":host, "error":str(r.exception or r.result)})
    else:
        report["succeeded"].append({"host": host})

with open (f"outputs/push_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
    json.dump(report, f, indent=2)

print(json.dumps(report, indent=2))