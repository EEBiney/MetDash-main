import pandas as pd

def load_data(data_file2):
    temp = pd.read_csv(data_file2, delimiter="\t", encoding="Latin1")
    return temp
