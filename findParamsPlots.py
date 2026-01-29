import matplotlib.pyplot as plt
import glob
import os
import statistics
import string
import numpy as np
from collections import defaultdict

list_of_files = glob.glob("Logs/*") # * means all if need specific format then *.csv

desired_file = sorted(list_of_files)[-1]
latest_file = max(list_of_files, key=os.path.getctime)

with open(desired_file) as f:
    lines = f.readlines()
    new_data = np.empty((len(lines), 4), dtype=object)
    row = 0
    for line in lines:
        str_indx = line.find("find")
        if str_indx != -1:
            new_line = line[str_indx:]
            str_r = new_line.find(r"\r")
            
            line_splitted = new_line[:str_r].split(";")

            new_data[row][0] = line_splitted[0]
            new_data[row][1] = line_splitted[1]
            new_data[row][2] = line_splitted[2]
            new_data[row][3] = line_splitted[3]
            row +=1

    new_data = new_data[:row]


groups = defaultdict(list)

for row in new_data:
    key = tuple(row[:3])      
    value = float(row[3])     
    groups[key].append(value)

plt.figure(figsize=(10, 6))

for key, y in groups.items():
    x = range(len(y))
    mean_y = np.mean(y)
    spread = max(y) - min(y)
    label = f"{key[0]}, {key[1]}, {key[2]}, mean = {mean_y}, spread = {(spread*5/1000)} mm"
    plt.plot(x, y, marker="o",markersize=4, linestyle='None', label=label)

plt.xlabel("Sample index (per group)")
plt.ylabel("Value")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()