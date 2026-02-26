import os
import re
import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


pathToFolder = r"c:\Users\KarolChudzicki\Desktop\Socket and logging\Certificates"

results = []

for file in os.listdir(pathToFolder):
    if file.endswith(".pdf"):
        
        full_path = os.path.join(pathToFolder, file)
        print(f"Processing: {file}")

        with pdfplumber.open(full_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()

                if text is None:
                    continue

                test_volume_match = re.findall(r"Test Volume.*?(-?\d+[\.,]?\d*)", text)


                # -------- FIND INACCURACY VALUES --------
                inaccuracy_matches = re.findall(
                    r"Inaccuracy.*?(-?\d+[\.,]?\d*)",
                    text
                )

                # -------- FIND IMPRECISION VALUES --------
                imprecision_matches = re.findall(
                    r"Imprecision.*?(-?\d+[\.,]?\d*)",
                    text
                )

                i = 0
                for value in inaccuracy_matches:
                    value = value.replace(",", ".")  # Replace comma with dot for decimal
                    results.append([file, page_number, "Inaccuracy", value, test_volume_match[i]])
                    i += 1

                i = 0
                for value in imprecision_matches:
                    value = value.replace(",", ".")  # Replace comma with dot for decimal
                    results.append([file, page_number, "Imprecision", value, test_volume_match[i]])
                    i += 1

# Convert to dataframe
df = pd.DataFrame(results, columns=["File", "Page", "Type", "Value", "Test Volume"])


# --------- EXPORT TO EXCEL ----------
output_path = pathToFolder + r"\extracted_results.xlsx"
df.to_excel(output_path, index=False)


print(df)









# Ensure numeric values
df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
df["Test Volume"] = pd.to_numeric(df["Test Volume"], errors="coerce")

# Extract Pipette names reliably from File
df["Pipette"] = df["File"].str.extract(r"(SMT\d+)")
df = df.dropna(subset=["Pipette"])  # drop rows without valid SMT

# Sort pipettes numerically
xaxis = sorted(df["Pipette"].unique(), key=lambda x: int(x[3:]))

# Volumes
volumes = [100, 50, 10]

# Pivot table with multiple rows per Pipette+Volume summed as mean if duplicates exist
pivot = df.pivot_table(index=["Pipette", "Test Volume"], columns="Type", values="Value", aggfunc="mean")

# ---------------- FIGURE 1: INACCURACY ----------------
fig1, axes = plt.subplots(1, 3, figsize=(20, 8), sharey=True)

for ax, volume in zip(axes, volumes):
    y_values = []
    for pipette in xaxis:
        try:
            y_values.append(pivot.loc[(pipette, volume), "Inaccuracy"])
        except KeyError:
            y_values.append(np.nan)
    
    for i, val in enumerate(y_values):
        if np.isnan(val):
            ax.plot(xaxis[i], 0, marker="o", color="none")
        else:
            ax.plot(xaxis[i], val, marker="o", color="blue")
    
    ax.set_title(f"{volume} %", fontsize=18)
    ax.set_xlabel("Pipette", fontsize=16)
    ax.axhline(0, color="gray", linestyle="--", alpha=0.7)
    ax.grid(True, linestyle=":", alpha=0.7)
    ax.tick_params(axis="both", labelsize=14)

axes[0].set_ylabel("Inaccuracy (d)", fontsize=16)
plt.tight_layout()

# ---------------- FIGURE 2: IMPRECISION ----------------
fig2, axes = plt.subplots(1, 3, figsize=(20, 8), sharey=True)

for ax, volume in zip(axes, volumes):
    y_values = []
    for pipette in xaxis:
        try:
            y_values.append(pivot.loc[(pipette, volume), "Imprecision"])
        except KeyError:
            y_values.append(np.nan)
    
    for i, val in enumerate(y_values):
        if np.isnan(val):
            ax.plot(xaxis[i], 0, marker="o", color="none")
        else:
            ax.plot(xaxis[i], val, marker="o", color="green")
    
    ax.set_title(f"{volume} %", fontsize=18)
    ax.set_xlabel("Pipette", fontsize=16)
    ax.axhline(0, color="gray", linestyle="--", alpha=0.7)
    ax.grid(True, linestyle=":", alpha=0.7)
    ax.tick_params(axis="both", labelsize=14)

axes[0].set_ylabel("Imprecision (CV)", fontsize=16)
plt.tight_layout()
plt.show()