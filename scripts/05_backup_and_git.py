from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result
import os 
import subprocess
from datetime import datetime 

nr = InitNornir(config_file="nornir_config.yaml")

def backup_config(task: Task) -> Result:
    output = task.run(
        task=netmiko_send_command,
        command_string="show running-config",
        enable=True
    )

    backup_dir = f"backups/{task.host.name}"
    os.makedirs(backup_dir, exist_ok=True)

    filepath = f"{backup_dir}/running_config.cfg"
    with open(filepath, "w") as f:
        f.write(output.result)

    return Result(host=task.host, result=f"Backed up to {filepath}")

result = nr.run(task=backup_config)
print_result(result)

subprocess.run(["git", "add", "backups/"], check=True)
subprocess.run([
    "git", "commit", "-m",
    f"chore: automated config backup {datetime.now().strftime('%Y-%m-%d %H:%M')}"
], check=True)

print("All configs backed up and commited to git")