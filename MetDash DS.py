import pandas as pd

df = pd.read_csv('data.csv')

#select columns 1 to 8 and make a new dataframe
df_metadata = df.iloc[:, 1:8]

#select columns 9 to ncol columns of df_data and make a new dataframe
df_data = df.iloc[:, 9:]

#select column 4 and use as the row names of df_data
df_data.index = df_metadata.iloc[:, 4]

#subtract the values in first row from other rows 
df_data = df_data.sub(df_data.iloc[0], axis=1)

#remove the first row afterwards
df_data = df_data.iloc[1:]

#make a scatter plot of the data with the first column as x representing the rownames and the rest of the columns as y
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
for column in df_data.columns:
    plt.scatter(df_data.index, df_data[column], label=column)
plt.xlabel('Samples')
plt.ylabel('Intensity')
plt.title('Metabolite Intensity Scatter Plot')
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()

plt.savefig('metabolite_scatter_plot.png')
# Show the plot
plt.show()
# Save the processed data to a new CSV file
df_data.to_csv('processed_df_data.csv')

