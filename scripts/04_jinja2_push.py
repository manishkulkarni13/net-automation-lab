from nornir import InitNornir
from nornir.core.task import Task, Result 
from nornir_netmiko.tasks import netmiko_send_config
from nornir_utils.plugins.functions import print_result
from jinja2 import Environment, FileSystemLoader
import os

nr = InitNornir(config_file="nornir_config.yaml")

def render_and_push(task: Task) ->Result:
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("loopback.j2")

    config = template.render(host=task.host)

    os.makedirs("outputs/rendered", exist_ok=True)
    with open(f"outputs/rendered/{task.host.name}_loopback.cfg", "w") as f:
        f.write(config)
    
    task.run(
        task=netmiko_send_config,
        config_commands=config.splitlines()
    )

    return Result(host=task.host, result=f"config pushed to {task.host.name}")

result = nr.run(task=render_and_push)
print_result(result)