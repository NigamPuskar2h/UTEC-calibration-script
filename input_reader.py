import pandas as pd 
from ruamel.yaml import YAML

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
    df_logger_acc = df.drop(["ArX", "ArY"], axis=1)
    return df_logger_acc

def ar_df(df):
    df_logger_ar = df.drop(["AccX", "AccY", "AccZ"], axis = 1)
    return df_logger_ar