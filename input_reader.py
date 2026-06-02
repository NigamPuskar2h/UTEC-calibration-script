import pandas as pd 
from ruamel.yaml import YAML

def read_input_yaml(input_yaml_file):
    yaml = YAML()
    yaml.preserve_quotes = True

    with open(input_yaml_file, "r") as f:
        InputYaml = yaml.load(f)

    class FilePaths:
        def __init__(self, path):
            self.logger = path["logger_path"]

    class InputConfig:
        def __init__(self, input_yaml):
            self.path = FilePaths(input_yaml["File Paths"])

    config = InputConfig(InputYaml)
    return config

def read_csv(file):
    df = pd.read_csv(file, header=None, names=["raw"])
    return df

def parse_logger(df):
    logger_df = df.iloc[:, 0].str.extractall(r'Result:\s*(?P<Result>[\d.E+-]+).*?').astype(float)
    logger_df = logger_df.unstack()

    #These names are not altered to reflect the actual values from the logger
    column_names = ({
        0: "ArX",
        1: "ArY", 
        2: "n/a", 
        3: "AccX", 
        4: "n/a", 
        5: "AccZ", 
        6: "AccY", 
        7: "AccT"
        })
    
    logger_df = logger_df.rename(columns = column_names)
    return logger_df

def clean_df(df):
    df = df.dropna(axis=0, how='any')
    return df
    