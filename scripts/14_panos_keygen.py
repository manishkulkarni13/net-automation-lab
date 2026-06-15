import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import xml.etree.ElementTree as ET
import os 

url = "https://192.168.177.50/api/"

data = {
    "type": "keygen",
    "user": os.environ["PANOS_USER"],
    "password": os.environ["PANOS_PASS"]
}

response = requests.post(url, data=data, verify = False, timeout=15)


root    = ET.fromstring(response.text)
print("keygen status:", root.attrib.get("status"))
key     = root.find(".//key").text 
print("KEY:", key[:6] + "...")
with open(".panos_key", "w") as f:
    f.write(key)

print("Key saved to .panos_key")
os.chmod(".panos_key", 0o600)
