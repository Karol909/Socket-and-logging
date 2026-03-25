import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ---------------- DATA ----------------
dataRobot1 = [
    ["SMT1", 100, -0.08168, 0.01111], ["SMT1", 50, -0.17723, 0.04616], ["SMT1", 10, 1.71886, 0.14160],
    ["SMT2", 100, 0.47911, 0.04726], ["SMT2", 50, -0.43738, 0.07400], ["SMT2", 10, -3.83164, 0.23824],
    ["SMT3", 100, 0.44279, 0.02585], ["SMT3", 50, -0.23978, 0.05074], ["SMT3", 10, -1.68038, 0.30265],
    ["SMT4", 100, 0.66443, 0.08021], ["SMT4", 50, -1.00021, 0.12147], ["SMT4", 10, -7.48487, 2.82982],
    ["SMT5", 100, 0.44038, 0.13686], ["SMT5", 50, -0.16354, 0.28663], ["SMT5", 10, -4.92670, 4.27017],
    ["SMT6", 100, 1.39142, 0.08020], ["SMT6", 50, 0.18756, 0.36561], ["SMT6", 10, -2.68960, 10.28061],
    ["SMT7", 100, -5.10730, 1.03137], ["SMT7", 50, -9.15020, 3.05676],
    ["SMT8", 100, -11.99920, 1.44960],
]

dataJette1 = [
    ["SMT3", 100, 0.01646, 0.08564],
    ["SMT3", 50, -0.1127, 0.09049],
    ["SMT3", 10, 0.82352, 0.15254],
    ["SMT4", 100, -0.06229, 0.08444],
    ["SMT4", 50, -0.3658, 0.20755],
    ["SMT4", 10, -1.61867, 0.26904],
    ["SMT5", 100, -0.22541, 0.11284],
    ["SMT5", 50, -0.4741, 0.18114],
    ["SMT5", 10, -1.0437, 0.41875],
    ["SMT6", 100, 0.73728, 0.06039],
    ["SMT6", 50, 0.5006, 0.23822],
    ["SMT6", 10, 0.6812, 0.84517],
    ["SMT7", 100, -0.2916, 0.3347],
    ["SMT7", 50, -1.7056, 0.99543],
    ["SMT7", 10, 1.985, 3.83357],
]

[
    ["SMT1", 100, -0.17100, 0.13591],
    ["SMT1", 50, -0.19874, 0.07124],
    ["SMT1", 10, 2.65964, 0.11390],
    ["SMT2", 100, -0.29184, 0.13589],
    ["SMT2", 50, -0.20287, 0.09247],
    ["SMT2", 10, 1.02167, 0.39363],
    ["SMT6", 100, 0.73728, 0.06039],
    ["SMT6", 50, 0.50060, 0.23822],
    ["SMT6", 10, 0.68120, 0.84517],
    ["SMT8", 100, -3.24980, 1.04268],
    ["SMT8", 50, -5.37560, 1.22127],
    ["SMT8", 10, -14.16000, 4.64358],
    ["SMT9", 100, -0.66183, 0.07354],
    ["SMT9", 50, -1.09303, 0.29071],
    ["SMT9", 10, 1.14240, 0.36158],
    ["SMT10", 100, -0.45946, 0.16724],
    ["SMT10", 50, -0.77896, 0.09571],
    ["SMT10", 10, 0.77740, 0.33120],
    ["SMT11", 100, -0.35116, 0.07441],
    ["SMT11", 50, -0.56396, 0.03126],
    ["SMT11", 10, 0.43844, 0.54280],
    ["SMT12", 100, 0.17270, 0.07496],
    ["SMT12", 50, -0.20334, 0.14482],
    ["SMT12", 10, 0.18970, 0.61840],
    ["SMT13", 100, -0.52525, 0.08054],
    ["SMT13", 50, -0.96948, 0.18487],
    ["SMT13", 10, 1.03210, 0.62480],
    ["SMT14", 100, -0.06496, 0.14255],
    ["SMT14", 50, -0.43600, 0.32765],
    ["SMT14", 10, 1.10230, 0.80168],
]

dataRobot2 = [
    ["SMT1", 100, -0.04258, 0.04863],
    ["SMT1", 50, -0.62112, 0.06648],
    ["SMT1", 10, -2.29599, 0.34623],
    ["SMT2", 100, 0.91365, 0.09938],
    ["SMT2", 50, 0.45336, 0.12576],
    ["SMT2", 10, 0.20499, 0.17137],
    ["SMT3", 100, 0.37206, 0.05400],
    ["SMT3", 50, -0.22822, 0.07949],
    ["SMT3", 10, -0.07298, 0.46604],
    ["SMT4", 100, -0.10641, 0.26099],
    ["SMT4", 50, -1.18409, 1.95994],
    ["SMT4", 10, -6.57913, 7.61363],
    ["SMT5", 100, 0.76235, 0.13814],
    ["SMT5", 50, -0.00480, 0.07916],
    ["SMT5", 10, -3.56070, 0.84284],
    ["SMT6", 100, 0.89572, 0.22584],
    ["SMT6", 50, -0.37784, 0.20152],
    ["SMT6", 10, -7.00040, 9.55867],
]


xaxis = ["SMT1", "SMT2", "SMT3", "SMT4", "SMT5", "SMT6", "SMT7", "SMT8"]
volumes = [100, 50, 10]

# Create DataFrames
dfrobot1 = pd.DataFrame(dataRobot1, columns=["Pipette", "Volume", "Inaccuracy", "CV"])
dfjette1 = pd.DataFrame(dataJette1   , columns=["Pipette", "Volume", "Inaccuracy", "CV"])
dfrobot2 = pd.DataFrame(dataRobot2, columns=["Pipette", "Volume", "Inaccuracy", "CV"])

# Full index
full_index = pd.MultiIndex.from_product([xaxis, volumes], names=["Pipette", "Volume"])

dfrobot1 = dfrobot1.set_index(["Pipette", "Volume"]).reindex(full_index).reset_index()
dfjette1 = dfjette1.set_index(["Pipette", "Volume"]).reindex(full_index).reset_index()
dfrobot2 = dfrobot2.set_index(["Pipette", "Volume"]).reindex(full_index).reset_index()

# -------- GLOBAL AXIS LIMITS --------
all_inaccuracy = pd.concat([dfrobot1["Inaccuracy"], dfjette1["Inaccuracy"], dfrobot2["Inaccuracy"]])
all_cv = pd.concat([dfrobot1["CV"], dfjette1["CV"], dfrobot2["CV"]])

ymin_acc, ymax_acc = all_inaccuracy.min(), all_inaccuracy.max()
ymin_cv, ymax_cv = all_cv.min(), all_cv.max()

# Add margin
margin_acc = 0.1 * (ymax_acc - ymin_acc)
margin_cv = 0.1 * (ymax_cv - ymin_cv)

# ---------------- FIGURE 1: INACCURACY ----------------
fig1, axes = plt.subplots(1, 3, figsize=(20, 8), sharey=True)

for ax, volume in zip(axes, volumes):
    s1 = dfrobot1[dfrobot1["Volume"] == volume]
    s2 = dfjette1[dfjette1["Volume"] == volume]
    s3 = dfrobot2[dfrobot2["Volume"] == volume]

    for i, (pipette, val) in enumerate(zip(xaxis, s1["Inaccuracy"])):
        if pd.isna(val):
            ax.plot(pipette, 0, marker="o", color="none")
        else:
            ax.plot(pipette, val, marker="o", color="blue")

    ax.plot(xaxis, s1["Inaccuracy"], "o-", label="Robot")
    ax.plot(xaxis, s2["Inaccuracy"], "s--", label="Jette")
    ax.plot(xaxis, s3["Inaccuracy"], "^:", label="Robot2")
    ax.set_title(f"{volume} % max volume", fontsize=18)
    ax.set_xlabel("Pipette", fontsize=16)
    ax.axhline(0, linestyle="--", alpha=0.7)
    ax.grid(True, linestyle=":", alpha=0.7)
    ax.set_ylim(ymin_acc - margin_acc, ymax_acc + margin_acc)

axes[0].set_ylabel("Inaccuracy (d)", fontsize=16)
axes[0].legend()
axes[1].legend()
axes[2].legend()
plt.tight_layout()

# ---------------- FIGURE 2: IMPRECISION ----------------
fig2, axes = plt.subplots(1, 3, figsize=(20, 8), sharey=True)

for ax, volume in zip(axes, volumes):
    s1 = dfrobot1[dfrobot1["Volume"] == volume]
    s2 = dfjette1[dfjette1["Volume"] == volume]
    s3 = dfrobot2[dfrobot2["Volume"] == volume]

    for i, (pipette, val) in enumerate(zip(xaxis, s1["CV"])):
        if pd.isna(val):
            ax.plot(pipette, 0, marker="o", color="none")
        else:
            ax.plot(pipette, val, marker="o", color="green")

    ax.plot(xaxis, s1["CV"], "o-", label="Robot")
    ax.plot(xaxis, s2["CV"], "s--", label="Jette")
    ax.plot(xaxis, s3["CV"], "^:", label="Robot2")

    ax.set_title(f"{volume} % max volume", fontsize=18)
    ax.set_xlabel("Pipette", fontsize=16)
    ax.grid(True, linestyle=":", alpha=0.7)
    ax.set_ylim(ymin_cv - margin_cv, ymax_cv + margin_cv)

axes[0].set_ylabel("Imprecision (CV)", fontsize=16)
axes[0].legend()
axes[1].legend()
axes[2].legend()
plt.tight_layout()
plt.show()