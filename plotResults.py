import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ---------------- DATA ----------------
data = [
    ["SMT1", 100, -0.08168, 0.01111], ["SMT1", 50, -0.17723, 0.04616], ["SMT1", 10, 1.71886, 0.14160],
    ["SMT2", 100, 0.47911, 0.04726], ["SMT2", 50, -0.43738, 0.07400], ["SMT2", 10, -3.83164, 0.23824],
    ["SMT3", 100, 0.44279, 0.02585], ["SMT3", 50, -0.23978, 0.05074], ["SMT3", 10, -1.68038, 0.30265],
    ["SMT4", 100, 0.66443, 0.08021], ["SMT4", 50, -1.00021, 0.12147], ["SMT4", 10, -7.48487, 2.82982],
    ["SMT5", 100, 0.44038, 0.13686], ["SMT5", 50, -0.16354, 0.28663], ["SMT5", 10, -4.92670, 4.27017],
    ["SMT6", 100, 1.39142, 0.08020], ["SMT6", 50, 0.18756, 0.36561], ["SMT6", 10, -2.68960, 10.28061],
    ["SMT7", 100, -5.10730, 1.03137], ["SMT7", 50, -9.15020, 3.05676],
    ["SMT8", 100, -11.99920, 1.44960],
]

xaxis = ["SMT1", "SMT2", "SMT3", "SMT4", "SMT5", "SMT6", "SMT7", "SMT8"]
volumes = [100, 50, 10]

# Create dataframe
df = pd.DataFrame(data, columns=["Pipette", "Volume", "Inaccuracy", "CV"])

# ---------------- FILL MISSING VALUES WITH NaN ----------------
full_index = pd.MultiIndex.from_product([xaxis, volumes], names=["Pipette", "Volume"])
df = df.set_index(["Pipette", "Volume"]).reindex(full_index).reset_index()

# ---------------- FIGURE 1: INACCURACY ----------------
fig1, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

for ax, volume in zip(axes, volumes):
    subset = df[df["Volume"] == volume]
    
    # Plot points: invisible if NaN
    for i, val in enumerate(subset["Inaccuracy"]):
        if pd.isna(val):
            ax.plot(xaxis[i], 0, marker="o", color="none")  # invisible point
        else:
            ax.plot(xaxis[i], val, marker="o", color="blue")  # visible point

    ax.set_title(f"{volume} µL")
    ax.set_xlabel("Pipette")
    ax.axhline(0, color="gray", linestyle="--", alpha=0.7)
    ax.grid(True, linestyle=":", alpha=0.7)

axes[0].set_ylabel("Inaccuracy (d)")
plt.tight_layout()

# ---------------- FIGURE 2: IMPRECISION ----------------
fig2, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

for ax, volume in zip(axes, volumes):
    subset = df[df["Volume"] == volume]
    
    for i, val in enumerate(subset["CV"]):
        if pd.isna(val):
            ax.plot(xaxis[i], 0, marker="o", color="none")  # invisible
        else:
            ax.plot(xaxis[i], val, marker="o", color="green")  # visible

    ax.set_title(f"{volume} µL")
    ax.set_xlabel("Pipette")
    ax.axhline(0, color="gray", linestyle="--", alpha=0.7)
    ax.grid(True, linestyle=":", alpha=0.7)

axes[0].set_ylabel("Imprecision (CV)")
plt.tight_layout()
plt.show()
