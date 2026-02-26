import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 🔹 CHANGE THIS TO YOUR FOLDER
folder_path = r"c:\Users\KarolChudzicki\Desktop\Socket and logging\Pipette dispense positions"

data = []

extra_labels = {
    "SMT1": "10000 uL",
    "SMT2": "5000 uL",
    "SMT3": "1000 uL",
    "SMT4": "300 uL",
    "SMT5": "200 uL",
    "SMT6": "100 uL",
    "SMT7": "20 uL",
    "SMT8": "10 uL",
    "SMT9": "1000 uL",
    "SMT10": "1000 uL",
    "SMT11": "1000 uL",
    "SMT12": "200 uL",
    "SMT13": "200 uL",
    "SMT14": "200 uL",
}




# ---------------- READ ALL FILES ----------------
for filename in os.listdir(folder_path):
    if filename.endswith(".txt"):
        
        name_part = filename.replace(".txt", "")
        parts = name_part.split()

        # Robust extraction
        try:
            smt_id = next(p for p in parts if p.startswith("SMT"))
            percent = next(p for p in parts if "%" in p).replace("%", "")
        except StopIteration:
            # Skip files that don't match pattern
            continue

        file_path = os.path.join(folder_path, filename)

        # Read numbers inside file
        with open(file_path, "r") as f:
            numbers = [float(line.strip()) for line in f if line.strip()]

        for number in numbers:
            data.append([smt_id, int(percent), number])

# Create dataframe
df = pd.DataFrame(data, columns=["SMT", "Percent", "Value"])

# Sort SMTs numerically (SMT1, SMT2, ..., SMT10 properly)
df["SMT_number"] = df["SMT"].str.extract(r"(\d+)").astype(int)
df = df.sort_values(["SMT_number", "Percent"])

# ---------------- PLOT 1 ----------------
fig, ax = plt.subplots(figsize=(12,7))

# Convert SMT to numeric positions
unique_smts = sorted(df["SMT"].unique(), key=lambda x: int(x.replace("SMT","")))
x_positions = {smt: i for i, smt in enumerate(unique_smts)}

for percent in sorted(df["Percent"].unique()):
    subset = df[df["Percent"] == percent]

    x_vals = [x_positions[s] for s in subset["SMT"]]
    
    means = subset.groupby("SMT")["Value"].mean()
    stds = subset.groupby("SMT")["Value"].std()

   

    if percent == 100:
        color = "#8B0000"   # dark red
        x_vals = np.array(x_vals) - 0.15
        mean_x = [x_positions[s] - 0.15 for s in means.index]
    elif percent == 50:
        color = "#E53935"   # medium red
        x_vals = np.array(x_vals)
        mean_x = [x_positions[s] for s in means.index]
    else:
        color = "#FFCDD2"   # light red
        x_vals = np.array(x_vals) + 0.15
        mean_x = [x_positions[s] + 0.15 for s in means.index]

    

    # ax.errorbar(
    #     mean_x,
    #     means.values,
    #     yerr=stds.values,
    #     fmt='none',
    #     ecolor=color,
    #     elinewidth=2,
    #     capsize=4
    # )

    ax.scatter(
        x_vals,
        subset["Value"],
        label=f"{percent}%",
        marker="o",
        s=60,
        color=color,
        edgecolor="black",
        alpha=0.8
    )

# Set proper x-axis labels
ax.set_xticks(range(len(unique_smts)))
combined_labels = [
    f"{smt}\n{extra_labels.get(smt, '')}"
    for smt in unique_smts
]

ax.set_xticklabels(combined_labels)

ax.set_xlabel("SMT ID", fontsize=12)
ax.set_ylabel("Blowout position (um)", fontsize=12)

overall_mean = df["Value"].mean()
mean10 = df[df["Percent"] == 10]["Value"].mean()
mean50 = df[df["Percent"] == 50]["Value"].mean()
mean100 = df[df["Percent"] == 100]["Value"].mean()

# ax.axhline(mean10, linestyle="", linewidth=1.2,
#            label=f"10% Mean = {mean10:.2f} µm")

# ax.axhline(mean50, linestyle="", linewidth=1.2,
#            label=f"50% Mean = {mean50:.2f} µm")

# ax.axhline(mean100, linestyle="", linewidth=1.2,
#            label=f"100% Mean = {mean100:.2f} µm")

ax.axvline(7.5, linestyle='-', color='blue', alpha=0.7)


xmin, xmax = ax.get_xlim()
ax.axhline(overall_mean, linestyle='--', color='gray', alpha=0.7)

ax.text(
    x=xmax-2,  # x-position (left side of plot)
    y=overall_mean + 5,  # small vertical offset (adjust if needed)
    s=f"Mean = {overall_mean:.2f} µm",
    fontsize=9,
    color="black",
    verticalalignment='bottom'
)


ax.legend(title="Volume (%)", fontsize=11, title_fontsize=12)
ax.grid(True, linestyle=":", alpha=0.6)

plt.tight_layout()
plt.show()


# # ---------------- PLOT 2 ----------------
# fig2, ax2 = plt.subplots(figsize=(12,7))

# # Take the first value for each combination of SMT and Percent
# first_points = df.groupby(["SMT", "Percent"]).first().reset_index()
# print(first_points)

# for percent in sorted(first_points["Percent"].unique()):
#     subset = first_points[first_points["Percent"] == percent]
#     x_vals = [x_positions[s] for s in subset["SMT"]]

#     if percent == 100:
#         x_vals = np.array(x_vals)
#         ax2.scatter(x_vals, subset["Value"], label=f"{percent}%", marker="o", s=60, color="blue", edgecolor="black", alpha=0.8)
        
#     # elif percent == 50:
#     #     x_vals = np.array(x_vals)
#     #     ax2.scatter(x_vals, subset["Value"], label=f"{percent}%", marker="o", s=60, color="orange", edgecolor="black", alpha=0.8)
#     # else:
#     #     x_vals = np.array(x_vals) + 0.1
#     #     ax2.scatter(x_vals, subset["Value"], label=f"{percent}%", marker="o", s=60, color="green", edgecolor="black", alpha=0.8)

# ax2.set_xticks(range(len(unique_smts)))
# ax2.set_xticklabels(combined_labels)
# ax2.set_xlabel("SMT ID", fontsize=12)
# ax2.set_ylabel("micro meters", fontsize=12)
# ax2.set_title("First point of each dataset", fontsize=14)
# ax2.legend(title="Volume (%)", fontsize=11, title_fontsize=12)
# ax2.grid(True, linestyle=":", alpha=0.6)

# plt.tight_layout()
# plt.show()
