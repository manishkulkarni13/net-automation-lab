import requests
import urllib3
import xml.etree.ElementTree as ET 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with open(".panos_key", "r") as f:
    key = f.read().strip()

url = "https://192.168.177.50/api/"

data = {
    "type": "config",
    "action": "set",
    "xpath" : ("/config/devices/entry[@name='localhost.localdomain']""/vsys/entry[@name='vsys1']/address/entry[@name='db-server']"),
    "element": "<ip-netmask>192.168.200.20/32</ip-netmask>",
    "key": key
     
}
response = requests.post(url, data=data, verify=False, timeout=15)
print(response.text)