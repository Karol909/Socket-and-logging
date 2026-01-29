import matplotlib.pyplot as plt
import glob
import os
import statistics
import numpy as np

list_of_files = glob.glob("Logs/*") # * means all if need specific format then *.csv

desired_file = sorted(list_of_files)[-1]
latest_file = max(list_of_files, key=os.path.getctime)

with open(desired_file) as f:
    lines = f.readlines()
    data = [int(line.split(',')[0]) for line in lines]

data = [x for x in data if x <= 10000]


data_mean = np.mean(data)
min_x = min(data)
max_x = max(data)
delta_um = 5 * (max_x - min_x)
std = np.std(data)

fig, axs = plt.subplots(1, 2, figsize=(10, 4))


axs[0].axline((0, data_mean), (len(data), data_mean), color='red')
axs[0].axline((0, max_x), (len(data), max_x), color='purple',  linestyle='--')
axs[0].axline((0, min_x), (len(data), min_x), color='purple', linestyle='--')
axs[0].plot(data, marker='o', markersize = 4, linestyle='None')
axs[0].grid()


text = (
    f"Min = {min_x} microsteps\n"
    f"Max = {max_x} microsteps\n"
    f"$\\Delta\\,\\mu m$ = {delta_um} $\\mu m$ = {(delta_um/1000)} mm\n"
    f"Std = {std:.4} microsteps\n"
    f"Std ($\\mu m$) = {(std*5):.4} $\\mu m$"
)
axs[0].text(
    0.02, 0.98, text,
    transform=axs[0].transAxes,
    verticalalignment='top',
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8)
)


axs[1].hist(data)
axs[1].grid()


plt.tight_layout()
plt.show()
