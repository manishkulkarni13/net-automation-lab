import requests
import urllib3
import time 
import sys 
import xml.etree.ElementTree as ET 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with open(".panos_key","r") as f:
    key = f.read().strip()

url = "https://192.168.177.50/api/"

# --- Part 1: submit the commit ---#

commit_data = {
    "type" : "commit",
    "cmd"  : "<commit></commit>",
    "key"  : key 
}

response = requests.post(url, data=commit_data, verify=False, timeout=30)
root = ET.fromstring(response.text)

job_el = root.find(".//job")
if job_el is None:
    print("Nothing to commit - candidate matches running.")
    sys.exit()

jobid = job_el.text
print(f"Commit submitted - job {jobid}")

# --- Part 2: poll the job untill it finishes ---

while True:
    time.sleep(2)
    poll_data = {
        "type":"op",
        "cmd" :f"<show><jobs><id>{jobid}</id></jobs></show>",
        "key" : key,
    }

    poll = requests.post(url, data=poll_data, verify=False, timeout=15)
    proot = ET.fromstring(poll.text)

    status = proot.find(".//job/status").text
    if status == "FIN":
        result = proot.find(".//job/result").text 
        print(f"Commit finished: {result}")
        break 
    
    progress = proot.find(".//job/progress").text 
    print(f" ...{progress}%")