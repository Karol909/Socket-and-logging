import os
import re
import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

certificateFolder = "CertificatesJette1"
pathToFolder = rf"c:\Users\KarolChudzicki\Desktop\Socket and logging\{certificateFolder}"



results = []

pdf_files = [f for f in os.listdir(pathToFolder) if f.endswith(".pdf")]

# Sort by SMT number
def extract_smt_number(filename):
    match = re.search(r"SMT(\d+)", filename)
    return int(match.group(1)) if match else float('inf')  # put unknown SMTs at the end

pdf_files_sorted = sorted(pdf_files, key=extract_smt_number)

print(pdf_files_sorted)

for file in pdf_files_sorted:
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


# Ensure numeric types
df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
df["Test Volume"] = pd.to_numeric(df["Test Volume"], errors="coerce")

# Extract SMT from filename
df["SMT"] = df["File"].str.extract(r"(SMT\d+)")

# Drop rows without SMT (if any)
df = df.dropna(subset=["SMT"])

# Pivot table to get Inaccuracy and Imprecision in columns
pivot = df.pivot_table(
    index=["SMT", "Test Volume"],
    columns="Type",
    values="Value",
    aggfunc="mean"  # average if multiple values
).reset_index()

# Optional: sort by SMT number and then volume descending
pivot["SMT_num"] = pivot["SMT"].str.extract(r"SMT(\d+)").astype(int)
pivot = pivot.sort_values(by=["SMT_num", "Test Volume"], ascending=[True, False])
pivot = pivot.drop(columns="SMT_num")

# Convert to list of lists (like dataJette1)
dataJette1 = pivot.values.tolist()


extracted_results_path = os.path.join(pathToFolder, f"extracted_{certificateFolder}.txt")
with open(extracted_results_path, "w") as f:
    f.write("[\n")
    volume = [100, 50, 10]
    i = 0
    for row in dataJette1:
        # Format numbers to 5 decimal places like your example
        row_str = f'["{row[0]}", {volume[i%3]}, {row[3]:.5f}, {row[2]:.5f}],\n'
        f.write(row_str)
        i += 1
    f.write("]\n")






