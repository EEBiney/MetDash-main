import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Import CSV table
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

# Plot raw results
plt.figure(figsize=(10, 6))
for i, col in enumerate(heights.columns):
    plt.plot(range(len(heights)), heights[col])
    plt.title(col)
    plt.savefig(f"plot_{i+1}.png")
    plt.clf()

# Remove unwanted metabolites
bad_metabolites = [
    "X.119..gamma.aminobutyric.acid..GABA...13.326..Results",
    "X.827..ribitol..15.66..Results",
    "X.C22..Methyl.Docosanoate..23.082..Results",
    "X.5962..L.lysine.2..17.643..Results",
    "X.439742..beta.cyano.L.alanine..11.288..Results"
]
heights = heights.drop(columns=[col for col in bad_metabolites if col in heights.columns])

# Remove sample with strange results
bad_sample = "240223_001"
if bad_sample in heights.index:
    heights = heights.drop(index=bad_sample)
    samp = samp[samp["Rawname"] != bad_sample]

# Export results
final = pd.concat([samp.reset_index(drop=True), heights.reset_index(drop=True)], axis=1)
final.to_csv("Thesis result table.txt", sep="\t", index=False)
