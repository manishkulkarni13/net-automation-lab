from nornir import InitNornir
from jinja2 import Environment, FileSystemLoader
import os

nr = InitNornir(config_file="nornir_config.yaml")

def rendered_template(host, template_name):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template(template_name)
    return template.render(host=host)


for host_name, host in nr.inventory.hosts.items():
    print(f"\n{'='*50}")
    print(f"HOST: {host_name}")
    print(f"{'='*50}")

    for template in ["base.j2", "interfaces.j2", "ospf.j2", "bgp.j2"]:
        rendered = rendered_template(host,template)
        print(f"\n---{template}---")
        print(rendered)

        os.makedirs("outputs/rendered", exist_ok=True)
        with open(f"outputs/rendered/{host_name}_{template}.cfg", "w") as f:
            f.write(rendered)
