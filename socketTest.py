import socket
import string
import time
import datetime
import os
from pathlib import Path

ROBOT_IP = "192.168.0.64"
PORT = 20001

log_name = "SMT3 calibration"

log_path_folder = Path("Pipette calibrations 25 Feb 2026")
log_path_folder.mkdir(parents=True, exist_ok=True)
disp_path_folder = Path("Pipette dispense positions")
disp_path_folder.mkdir(parents=True, exist_ok=True)
txt_file_name = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S") + f" {log_name}.txt"

log_path = (log_path_folder / txt_file_name)


disp_log_path = (disp_path_folder / txt_file_name)

with open(log_path, "w", encoding="utf-8") as f:
    f.write("")

with open(disp_log_path, "w", encoding="utf-8") as f:
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
s.settimeout(.1)

data = bytearray()
while True:
    try:
        r = s.recv(4096)
        t_recv = time.time()
        if not r:
            print("Connection closed by robot")
            raise ConnectionError()
        if len(data) == 0:
            print(f"New data incoming", end="", flush=True)
        else:
            print(f".", end="", flush=True)
        data.extend(r)
    except socket.timeout:
        if len(data) > 0:
            print()
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S  ")+f"Received {len(data)} bytes:")
            msg = data.decode("utf-8")
            # if "buffer (" in msg:
            #     i0 = msg.index("buffer (")
            #     print("TEST", i0, msg)
            #     msg = msg[:i0+30] + " ... " + msg[i0+msg[i0:].index(")")-30:]
            
            foundDispPosition = msg.find("Found dispense position:")
            if foundDispPosition != -1:
                foundNewline = msg.find("\r\n", foundDispPosition, foundDispPosition+50)
                dispPosition = msg[foundNewline-5:foundNewline]
                print(f"============ {dispPosition} um ============")
                with open(disp_log_path, "a", encoding="utf-8") as f:
                    f.write(dispPosition + "\n")


                
                

            print(msg)
            
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(str(data) + ", " + datetime.datetime.now().strftime("%H:%M:%S") + "\n")

            
            data = bytearray()

    except Exception as e:
        print("Connection error, reconnecting...", e)
        s.close()
        s = connect()
