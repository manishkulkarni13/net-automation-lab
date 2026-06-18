from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_netmiko.tasks import netmiko_send_config, netmiko_send_command
from nornir_utils.plugins.functions import print_result
import sys, os
#When you run 'python3 scripts/18_.....py', sys.path[0] is scripts/, NOT the repo root,
#so 'lib' wouldnt be found. This line adds the repo root(parent of scripts/)
#to the import path so 'from lib...' works no matter where you launch from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.gitops import git_commit

nr = InitNornir(config_file="nornir_config.yaml")
MODEL_CMD = "service routing protocols model multi-agent"

def ensure_multiagent(task: Task) -> Result:
    # pre-check: is it already multi-agent?
    current = task.run(
        task=netmiko_send_command,
        command_string="show running-config | include service routing protocols model",
    )
    if "multi-agent" in current.result:
        return Result(host=task.host, result=f"{task.host.name}: already multi-agent — skip", changed=False)

    task.run(task=netmiko_send_config, config_commands=[MODEL_CMD])
    task.run(task=netmiko_send_command, command_string="write memory")
    return Result(host=task.host, result=f"{task.host.name}: set + saved — RESTART REQUIRED", changed=True)

ceos = nr.filter(platform="eos")
result = ceos.run(task=ensure_multiagent)
print_result(result)

# only the nodes that actually changed need a restart
to_restart = [host for host, mr in result.items() if mr.changed]
print("Restart these:", to_restart)

#commit the script itself + any config backups as the audit trail for this change
git_commit(
    ["scripts/18_multiagent_model.py"],
    "Enable multi-agent routing model on cEOS fabric",
)