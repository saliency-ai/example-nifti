import requests
import time
import urllib.request
import sys
from pprint import pprint

if len(sys.argv) < 4:
    exit("Error: This script takes 3 arguments: username, password and file path")

username=sys.argv[1]
password=sys.argv[2]
filename=sys.argv[3]

HOST_URL="https://api.saliency.ai/"

print("Logging in.")
r = requests.post(HOST_URL + "api-auth/token/", data = {
    "username": username, "password": password
})
if not r:
    exit("Error: Check your username and password")
    
token = r.json()["token"]
print("[OK]")

print("Uploading {}.".format(filename))
with open(filename, "rb") as f:
    r = requests.post(HOST_URL + "datapoints/",
                      data = {
                          "filename": filename
                      },
                      files = {
                          "file": (filename, f, "image/nii")
                      },
                      headers = {
                          "Authorization": "Token {}".format(token)
                      })
    if not r:
        exit("Error while uploading a file (too big?)")
print("[OK]")

print("Running a function on the uploaded datapoint. This can take a while.")
done = False
for i in range(20):
    r = requests.get(HOST_URL + "datapoints/{}/predict/?model=body_part_regressor.tasks.coverage".format(r.json()["id"]), headers = {"Authorization": "Token {}".format(token)})
    rd = r.json()
    if rd["status"] == "done":
        done = True
        break
    print(".", end="")
    time.sleep(6)

if not done:
    exit("Error: Timeout -- the function took too long to compute")

print("[OK]")

print("Results:")
pprint(rd)

print("Downloading {} to output.png.".format(rd["file"]))
urllib.request.urlretrieve(rd["file"], 'output.png')
print("[OK]")
