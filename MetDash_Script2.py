import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import entropy

# Load data
temp = pd.read_csv("data.csv", encoding="Latin1")

# Extract height data
heights = temp.iloc[:, 7:]
heights.index = temp.iloc[:, 3].str.replace(".D", "", regex=False)
heights = heights.iloc[1:, :]

# Import sample metadata
# create a text file with Sample and Rawname as 1st and 2nd columns and additional columns 
# with tretment and weight information
# The Rawname and Samlple columns can be extracted from the height.csv file
# Remember to delete the ".D"
samp = pd.read_csv("Sample_info.txt", sep="\t")
samp.columns.values[1] = "Sample"

# Merge Rawname
heights["Rawname"] = heights.index
heights = pd.merge(heights, samp[["Rawname"]], on="Rawname")
rawnames = heights["Rawname"]
heights = heights.drop(columns=["Rawname"])
heights = heights.apply(pd.to_numeric, errors='coerce')
heights.index = rawnames

# Calculate BK values and filter
BK_indices = samp[samp["Sample"].str.contains("BLK")].index
BK = heights.iloc[BK_indices].mean(skipna=True).values
BK = np.nan_to_num(BK)

medi = heights.median(skipna=True)
medi_bk = medi - BK
valid_cols = (medi_bk / BK > 0.2)
heights = heights.loc[:, valid_cols]
BK = BK[valid_cols.values]

# Subtract BK from each row
heights = heights.apply(lambda row: row - BK, axis=1)

# Normalize by ribitol
ribitol_cols = heights.columns[heights.columns.str.contains("ribitol")]
rib = heights[ribitol_cols]

if not (rib == 0).all().all():
    heights = heights.div(rib.values, axis=0)

# 📊 Step 1: Plot all raw results
os.makedirs("raw_plots", exist_ok=True)
for i, col in enumerate(heights.columns):
    plt.figure()
    plt.plot(range(len(heights)), heights[col])
    plt.title(f"Raw Plot: {col}")
    plt.xlabel("Sample Index")
    plt.ylabel("Intensity")
    plt.tight_layout()
    plt.savefig(f"raw_plots/{col}.png")
    plt.close()

# 🔍 Step 2: Define distribution filter
def is_evenly_distributed(y_values, bins=10, threshold=0.6):
    hist, _ = np.histogram(y_values, bins=bins)
    hist = hist + 1e-6
    dist_entropy = entropy(hist)
    max_entropy = np.log(bins)
    normalized_entropy = dist_entropy / max_entropy
    return normalized_entropy > threshold

# 🧹 Step 3: Filter evenly distributed plots
even_columns = []
for col in heights.columns:
    y = heights[col].values
    if is_evenly_distributed(y):
        even_columns.append(col)

# 📄 Step 4: Combine selected plots into a PDF
with PdfPages("evenly_distributed_plots.pdf") as pdf:
    for col in even_columns:
        plt.figure()
        plt.plot(range(len(heights)), heights[col])
        plt.title(f"Even Distribution: {col}")
        plt.xlabel("Sample Index")
        plt.ylabel("Intensity")
        plt.tight_layout()
        pdf.savefig()
        plt.close()
