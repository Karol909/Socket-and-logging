import matplotlib.pyplot as plt
import glob
import os
import statistics
import numpy as np
import pandas as pd
import sys

list_of_files = glob.glob("Logs/*") # * means all if need specific format then *.csv

good_idx = [1,2,3,5,8,9,11,36]

run_idx = sys.argv[1].split(',') if len(sys.argv) > 1 else [good_idx[-1]]

for r_idx in run_idx:
    desired_file = sorted(list_of_files)[good_idx[int(r_idx)]]
    name = desired_file.split("\\")[-1][18:].replace(".txt","").replace(" ","-")
    timestamp = desired_file.split("\\")[-1][:18].replace(" ", "_")
    name_parts = name.split("_")
    pip = name_parts[0]
    vol = name_parts[1] if len(name_parts) > 1 else "n/a"
    target = name_parts[2] if len(name_parts) > 2 else "n/a"
    print(f"{pip} ({vol}) @ {target}")

    latest_file = max(list_of_files, key=os.path.getctime)

    with open(desired_file) as f:
        lines = f.readlines()
        # data = [int(line.split(',')[0]) for line in lines]

    data = []
    dt = []
    itr = []
    win = []
    for l in lines:
        if l.startswith('bytearray'):
            if 'return;find;' in l:
                s = l.split('return;find;')[1].split(';')
                win.append(int(s[0]))
                itr.append(int(s[1]))
                data.append(int(s[2].split("\\")[0]))
                dt.append(l.strip()[-8:])
        else:
            s = l.split(',')
            d = int(s[0])
            if d > 10000: continue # not a step, but µm value
            data.append(d)
            dt.append(s[1].strip())
            win.append(20 if "2026-01-27" in desired_file else 10)
            itr.append(3 if "2026-01-27" in desired_file else 5)

    if len(data) < 10:
        print(f"not enough data: {desired_file}")
        exit()

    df = pd.DataFrame({'step': data, 'win': win, 'itr': itr, 'dt': dt})

    # group by mode
    groups = df.groupby(['win', 'itr']).apply(lambda g: g.index.to_numpy())
    for i in range(len(groups)):
        win, iter = groups.index[i]
        data = df['step'].iloc[groups.iloc[i]]
        data = data[data != 0]
        if len(data) < 10:
            print(f'not enough data {name}, win:{win}, iter:{iter}')
            continue
        x = np.arange(len(data))


    # data = [x for x in data if x <= 10000]


        data_mean = np.mean(data)
        min_x = min(data)
        max_x = max(data)
        delta_um = 5 * (max_x - min_x)
        std = np.std(data)

        fig, axs = plt.subplots(1, 2, figsize=(12, 6))
        fig.suptitle(f"{name}; win: {win}, iter: {iter}")

        axs[0].axline((0, data_mean), (len(data), data_mean), color='red')
        axs[0].axline((0, max_x), (len(data), max_x), color='purple',  linestyle='--')
        axs[0].axline((0, min_x), (len(data), min_x), color='purple', linestyle='--')
        axs[0].plot(x,data, marker='o', markersize = 4, linestyle='None')
        axs[0].grid()


        text = (
            f"Mean = {data_mean:.2f} microsteps\n"
            f"Min = {min_x} microsteps\n"
            f"Max = {max_x} microsteps\n"
            f"$\\Delta\\,\\mu m$ = {delta_um} $\\mu m$ = {(delta_um/1000)} mm\n"
            f"Std = {std:.4} microsteps\n"
            f"Std ($\\mu m$) = {(std*5):.4} $\\mu m$"
        )

        axs[1].hist(data)
        axs[1].text(
            0.02, 0.98, text,
            transform=axs[1].transAxes,
            verticalalignment='top',
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8)
        )
        axs[1].grid()


        plt.tight_layout()
        plt.savefig(f'Plots/{timestamp}_{name}_{i}.png')
plt.show()
