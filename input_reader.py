import pandas as pd 
from ruamel.yaml import YAML

def read_input_yaml(input_yaml_file):
    yaml = YAML()
    yaml.preserve_quotes = True

    with open(input_yaml_file, "r") as f:
        InputYaml = yaml.load(f)

    class DataInputs:
        def __init__(self, data):
            self.region = data["region"]
            self.res_freq_col = data["resonant_freq_column"]
            self.bin_size = data["bin_size"]

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
    csv = pd.read_csv(file)
    print(csv)
