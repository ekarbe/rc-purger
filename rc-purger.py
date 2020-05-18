import requests
import getpass
from time import sleep
from tqdm import tqdm
import math

host = input("Host: ")
username = input("Username: ")
try:
    password = getpass.getpass()
except Exception as error:
    print(error)

url = host + "/api/v1/login"
payload = {"user": username, "password": password}
r = requests.post(url, data=payload)
r = r.json()
if r["status"] != "success":
    print("Login failed!")
    exit()
authToken = r["data"]["authToken"]
userId = r["data"]["userId"]

url = host + "/api/v1/im.list"
headers = {'X-Auth-Token': authToken, 'X-User-Id': userId}
r = requests.get(url, headers=headers)
ims = r.json()

for im in ims["ims"]:
    print("Room ID: " + im["_id"] + "\n\nParticipents: ")
    print(im["usernames"])
    print("\nMessagecount: " + str(im["msgs"]))
    print("\nEstimated time: " + str(((im["msgs"]/2) * 6) / 60) + " minutes")
    print("\n-----------------------------------------------------")

roomId = input("Target Room ID: ")

url = host + "/api/v1/im.history?roomId=" + roomId + "&count=100"
r = requests.get(url, headers=headers)
his = r.json()
if(his["success"] == False):
    print("Error while getting history!")
    print(his)
    exit()

url = host + "/api/v1/im.counters?roomId=" + roomId
r = requests.get(url, headers=headers)
msgs = r.json()["msgs"]
if(msgs == None):
    print("No messages found!")
    exit()

for i in tqdm(range(math.ceil(msgs/100))):
    latest = his["messages"][-1]["ts"]
    for msg in tqdm(his["messages"]):
        if msg["u"]["_id"] == userId:
            url = host + "/api/v1/chat.delete"
            data = {"roomId": roomId, "msgId": msg["_id"]}
            success = requests.post(url, data=data, headers=headers)
            if(success.json()["success"] == False):
                print("Something went wrong!")
                print(success.json())
            sleep(6)
    sleep(15)
    url = host + "/api/v1/im.history?roomId=" + \
        roomId + "&count=100&latest=" + latest
    r = requests.get(url, headers=headers)
    his = r.json()
    if(his["success"] == False):
        print("Error while getting history!")
        print(his)
        exit()

print("Finished the great purge.")
