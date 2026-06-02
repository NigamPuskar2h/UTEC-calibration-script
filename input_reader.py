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
            if v == "n/a"
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
    df = pd.read_csv(file, header=None, names=["raw"])
    return df

def parse_logger(df, config):
    logger_df = df.iloc[:, 0].str.extractall(r'Result:\s*(?P<Result>[\d.E+-]+).*?').astype(float)
    logger_df = logger_df.unstack()
    logger_df.columns = logger_df.columns.get_level_values(1)
    
    column_names = config.data.original_logger_headings
    logger_df = logger_df.rename(columns = column_names)

    return logger_df

def format_logger_df(df, config):
    cols_to_remove = list(config.data.remove_logger_headings.values())
    format_logger_df = df.drop(columns = cols_to_remove)
    format_logger_df = format_logger_df.sort_index(axis=1)
    return format_logger_df

def clean_df(df):
    df = df.dropna(axis=0, how='any')
    return df

