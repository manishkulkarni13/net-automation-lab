from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result
import sys, os
# same bootstrap as 18: add repo root (parent of scripts/) to the import path
# so 'from lib...' resolves no matter where you launch from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.gitops import git_commit
# NOTE: subprocess + datetime imports are GONE — that logic now lives in gitops.py

nr = InitNornir(config_file="nornir_config.yaml")


def backup_config(task: Task) -> Result:
    output = task.run(
        task=netmiko_send_command,
        command_string="show running-config",
        enable=True,
    )

    backup_dir = f"backups/{task.host.name}"      # one folder per device
    os.makedirs(backup_dir, exist_ok=True)        # exist_ok=True -> no crash on re-run

    filepath = f"{backup_dir}/running_config.cfg"
    with open(filepath, "w") as f:                # 'with' auto-closes the file
        f.write(output.result)

    return Result(host=task.host, result=f"Backed up to {filepath}")


if __name__ == "__main__":                        # only runs when 05 is executed directly
    result = nr.run(task=backup_config)
    print_result(result)

    # one idempotent call replaces the two inline subprocess calls.
    # safe to re-run: if nothing changed, git_commit prints "nothing to commit"
    # instead of crashing — which the old check=True commit would have done.
    git_commit(["backups/"], "chore: automated config backup")