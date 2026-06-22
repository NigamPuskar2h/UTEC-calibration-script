import pandas as pd 
from ruamel.yaml import YAML
from datetime import datetime

def read_input_yaml(input_yaml_file):
    yaml = YAML()
    yaml.preserve_quotes = True

    with open(input_yaml_file, "r") as f:
        InputYaml = yaml.load(f)
    class DataInputs:
        def __init__(self, data):
            self.original_logger_headings = data["logger_headings"] 
            
            self.remove_logger_headings = {
            k: v for k, v in self.original_logger_headings.items()
            if v == None
        }

    class FilePaths:
        def __init__(self, path):
            self.logger = path["logger_path"]

    class InputConfig:
        def __init__(self, input_yaml):
            self.data = DataInputs(input_yaml["Data Inputs"])
            self.path = FilePaths(input_yaml["File Paths"])

    config = InputConfig(InputYaml)
    return config 

def read_csv(file):
    df = pd.read_csv(file, header=None)
    return df

def read_xlsx(file, sheet_index):
    df = pd.read_excel(file, sheet_name=sheet_index, header=0)
    return df

def clean_df(df):
    df = df.dropna(axis=0, how='any')
    return df

def acc_df(df):
    cols_to_remove = ["ArX", "ArY", "ARXY", "ARZ"]
    df_logger_acc = df.drop(columns = cols_to_remove, errors="ignore")
    return df_logger_acc

def ar_df(df):
    df_logger_ar = df.drop(["AccX", "AccY", "AccZ"], axis=1)
    return df_logger_ar

def extract_start_logger(df):
    start_val = (pd.to_timedelta(df.iloc[0,0]).value - 1) // 1_000_000 #Minus 1 because of rounding error when parsing
    return start_val
'''
def extract_start_logger(df):
    td = pd.to_timedelta(df.iloc[0,0])
    time_ms = int(td.total_seconds()*1000) -1 #Minus 1 because of rounding error when parsing
    return time_ms
'''