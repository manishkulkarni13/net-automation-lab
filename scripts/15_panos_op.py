import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import xml.etree.ElementTree as ET 


with open(".panos_key", "r") as f:
    key = f.read().strip()

#print("Loaded key:", key[:6] + "...")

url = "https://192.168.177.50/api/"

data = {
    "type":"op",
    "key" : key,
    #"cmd" : "<show><system><info></info></system></show>"
    #"cmd": "<check><pending-changes></pending-changes></check>",
    #"cmd": "<show><jobs><type>Commit</type></jobs></show>"
    "cmd": "<show><jobs><all></all></jobs></show>"
    
}

response = requests.post(url, data=data, verify=False, timeout=15)
print(response.text)

#root = ET.fromstring(response.text)
#hostname = root.find(".//hostname").text
#model    = root.find(".//model").text
#version  = root.find(".//sw-version").text

#print(f"{hostname} - {model} - {version}")