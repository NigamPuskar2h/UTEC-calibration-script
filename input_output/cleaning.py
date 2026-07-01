import pandas as pd 
from ruamel.yaml import YAML

def df_clean(num_sheets, sheet_index, df):
    df_cleaned = {}
    for i in range(num_sheets):
        key = sheet_index[i]
        values = df[key]
        df_cleaned[key] = values.dropna(axis=0, how='any')
    return(df_cleaned)

def acc_df(df):
    cols_to_remove = ["ArX", "ArY", "ARXY", "ARZ"]
    df_logger_acc = df.drop(columns = cols_to_remove, errors="ignore")
    return df_logger_acc

def ar_df(df):
    df_logger_ar = df.drop(["AccX", "AccY", "AccZ"], axis=1)
    return df_logger_ar
