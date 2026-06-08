 # Import the main Nornir class used to initialize and managed the automation framework
from nornir import InitNornir                      

# Import Task and Result classes - these are the building blocks for defining custom tasks
from nornir.core.task import Task, Result  

# Import the netmiko task that sends configuration commands to network devices via ssh
from nornir_netmiko.tasks import netmiko_send_config

# Import helper function to print nicely formatted results after running tasks
from nornir_utils.plugins.functions import print_result 

# Import Jinja2 components needed to load and render configuration templates.
from jinja2 import Environment, FileSystemLoader

#Import Python's built-in os module to work with directories and files (eg saving rederened configs)
import os

# Create the Nornir object by reading the configuration file.
#This loads inventory (hosts, groups), defaults, and connection settings.
nr = InitNornir(config_file="nornir_config.yaml")


# Define a helper function to render Jinja2 templates for a specific host
def render_template(host, template_name):

    #Create a Jinja2 Environment object and tell it where to find the template files.
    env = Environment(loader=FileSystemLoader("templates"))

    # Load the specific template file (eg base.j2) from templates folder
    template = env.get_template(template_name)

    # Render (fill in) the template using the host's data and return the resulting text
    return template.render(host=host)


# Main task function that will be executed on every device in the inventory
def day0_config(task:Task) -> Result:

    # Initialize an empty list to collect all rendered configuration sections
    configs = []


    #Loop through each template we want to render for Day 0 configuration
    for templates in ["base.j2","interfaces.j2", "ospf.j2", "bgp.j2"]:

        #Render the current template using this device's variables
        rendered = render_template(task.host, templates)

        #Add the rendered config to our list so we can combine them later
        configs.append(rendered)


        #Ensure the output directory for this hosts exists (creates it if missing)
        os.makedirs(f"outputs/rendered/{task.host.name}", exist_ok=True)

        #Save the rendered template to a file for review/audit/troubleshooting
        with open(f"outputs/rendered/{task.host.name}/{templates}.cfg", "w") as f:
            f.write(rendered)
    

    #Join all the rendered configuration sections into one large config block
    full_config = "\n".join(configs)

    #Execute the netmiko task to connect to the device and apply the full configuration
    #config_commands expects a list of strings, so we split the big string by newlines
    task.run(
        task=netmiko_send_config,
        config_commands=full_config.splitlines()
    )


    #Return a Result object with a success message for this host
    return Result(host=task.host, result=f"Day0 config pushed to {task.host.name}")


# Run the day0_config task on ALL hosts defined in the inventory (in parallel)
result = nr.run(task=day0_config)

#Print a formaated summary of the execution results (success, failure, output per device)
print_result(result)