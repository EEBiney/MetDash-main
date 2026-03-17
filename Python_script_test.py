import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")   # Use non-GUI backend for Flask
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def load_data(data_file, sample_file):
    temp = pd.read_csv(data_file, encoding="Latin1")
    samp = pd.read_csv(sample_file, sep="\t")
    samp.columns.values[0] = "Sample"
    return temp, samp

def process_heights(temp, samp):
    # Extract height data
    heights = temp.iloc[:, 7:]
    heights.index = temp.iloc[:, 3].str.replace(".D", "", regex=False)
    heights = heights.iloc[1:, :]

    # Merge Rawname
    heights["Rawname"] = heights.index
    heights = pd.merge(heights, samp[["Rawname"]], on="Rawname")
    rawnames = heights["Rawname"]
    heights = heights.drop(columns=["Rawname"])
    heights = heights.apply(pd.to_numeric, errors='coerce')
    heights.index = rawnames
    return heights

def subtract_blank(heights, samp):
    BK_indices = samp[samp["Sample"].str.contains("BK")].index
    BK = heights.iloc[BK_indices].mean(skipna=True).values
    BK = np.nan_to_num(BK)

    medi = heights.median(skipna=True)
    medi_bk = medi - BK
    valid_cols = (medi_bk / BK > 0.2)
    heights = heights.loc[:, valid_cols]
    BK = BK[valid_cols.values]

    # Subtract BK from each row
    heights = heights.apply(lambda row: row - BK, axis=1)
    return heights, BK

def normalize_ribitol(heights):
    ribitol_cols = heights.columns[heights.columns.str.contains("ribitol")]
    rib = heights[ribitol_cols]
    if not (rib == 0).all().all():
        heights = heights.div(rib.values, axis=0)
    return heights

def clean_data(heights, samp):  
    bad_metabolites = [
        "[C4] Methyl Butanoate [6.016] Results",
        "[C8] Methyl Caprylate [7.812] Results",
        "[C9] Methyl Pelargonate [9.248] Results",
        "[C10] Methyl Caprate [10.647] Results",
        "[C12] Methyl Laurate [13.250] Results",
        "[C14] Methyl Myristate [15.597] Results",
        "[C16] Methyl Palmitate [17.723] Results",
        "[C20] Methyl Eicosanoate [21.441] Results",
        "[C22] Methyl Docosanoate [23.082] Results",
        "[C24] Methyl Linocerate [24.603] Results",
        "[C26] Methyl Hexacosanoate [26.023] Results",
        "[C28] Methyl Octacosanoate [27.349] Results",
        "[C30] Methyl Triacontanoate [28.723] Results"
    ]

    # Drop bad metabolites if they exist
    cols_to_drop = [
        col for col in heights.columns
        if any(bad_met in col for bad_met in bad_metabolites)
    ]
    heights = heights.drop(columns=cols_to_drop)

    # Drop rows where Sample contains "Blank"
    samp_clean = samp[~samp["Sample"].str.contains("Blank", case=False, na=False)]
    heights_clean = heights.loc[samp_clean["Rawname"]]
    
    return heights_clean, samp_clean

def plot_results(heights, samp, outfile="plots/all_plots.pdf"): 
    # Ensure output directory exists
    outdir= os.path.dirname(outfile)
    if outdir and not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=True)

    # Get the Sample names for plotting labels
    sample_names = samp["Sample"].tolist()
    
    # Create a single PDF file to store all plots
    with PdfPages(outfile) as pdf:
        for col in heights.columns:
            plt.figure(figsize=(10, 6))
            
            # Use the positional index (0, 1, 2...) for the scatter plot
            # and the 'Sample' names for the labels.
            x_positions = range(len(heights))
            
            # Use cleaned data for plotting
            plt.scatter(x_positions, heights[col], s=10, color='blue')
            
            plt.title(col)
            plt.xlabel("Sample")
            plt.ylabel("Normalized intensity")
            
            # Set the x-axis ticks to the Sample names
            plt.xticks(x_positions, sample_names, rotation=90, fontsize=6) 
            
            plt.tight_layout() # Adjust layout to prevent labels from being cut off
            pdf.savefig()   # saves the current figure into the PDF
            plt.close()

def export_results(heights, samp, outfile="Thesis result table.txt"):
    final = pd.concat([samp.reset_index(drop=True), heights.reset_index(drop=True)], axis=1)
    final.to_csv(outfile, sep="\t", index=False)
    return final

def main(data_file="data.csv", sample_file="Sample_info.txt", REPORTS_FOLDER="reports"):
    temp, samp = load_data(data_file, sample_file)
    heights = process_heights(temp, samp)
    heights, BK = subtract_blank(heights, samp)
    heights = normalize_ribitol(heights)
    heights, samp = clean_data(heights, samp)
    plot_results(heights, samp, outfile=os.path.join(REPORTS_FOLDER, "test_plots.pdf"))
    final = export_results(heights, samp, outfile=os.path.join(REPORTS_FOLDER, "test_results.txt"))
    return final

if __name__ == "__main__":
    main()