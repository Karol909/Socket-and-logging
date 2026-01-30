import socket
import time
import datetime
import os
from pathlib import Path

ROBOT_IP = "192.168.0.64"
PORT = 20001

pipette = "P22795J"
maxvolume = 1000
volume = 100 #In percents

log_path_folder = Path("Logs")

log_path_folder.mkdir(parents=True, exist_ok=True)

txt_file_name = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S") + f" {pipette}_{maxvolume}uL_{volume}%.txt"

log_path = (log_path_folder / txt_file_name)

with open(log_path, "w", encoding="utf-8") as f:
    f.write("")

def connect():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ROBOT_IP, PORT))
            print("Connected to", ROBOT_IP, PORT)
            return s
        except Exception as e:
            print("Connection failed, retrying...", e)
            time.sleep(1)

s = connect()

data = bytearray()
while True:
    try:
        r = s.recv(4096)
        if not r:
            print("Connection closed by robot")
            raise ConnectionError()
        print(f"received {len(r)} bytes", r)
        data.extend(r)
        if data[-1] == b'\n'[0]:
            # print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S  ")+f"Received bytes ({len(data)}, {len(str(data).split(';'))-2}):", data)
            # if 
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(str(data) + ", " + datetime.datetime.now().strftime("%H:%M:%S") + "\n")
            # message = str(data).strip().split(';')

            # message.pop(0)

            # for msg in message:
            #     msg.strip()
            # print(message[0])
            # submessages = str(message).strip().split(' ')
            # if message[0] == "find":
            #     position = message[-1][:4]
            #     print("Position found - " + position)
            #     with open(log_path, "a", encoding="utf-8") as f:
            #         f.write(position + ", " + datetime.datetime.now().strftime("%H:%M:%S") + "\n")
            # elif submessages[0][2:] == "found":
            #     position = submessages[3][:5]
            #     print("Position found um - " + position)
            #     with open(log_path, "a", encoding="utf-8") as f:
            #         f.write(position + ", " + datetime.datetime.now().strftime("%H:%M:%S") + "\n")

            
            
            data = bytearray()


    except socket.timeout:
        pass
    except Exception as e:
        print("Connection error, reconnecting...", e)
        s.close()
        s = connect()
