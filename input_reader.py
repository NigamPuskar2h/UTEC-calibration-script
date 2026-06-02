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
    df = pd.read_csv(file)
    return df
