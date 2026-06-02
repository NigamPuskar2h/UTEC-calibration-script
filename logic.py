import input_reader

def main_logic():
    config = input_reader.read_input_yaml(r"Input.yaml")
    file = config.path.logger
    df = input_reader.read_csv(file)
    print(df)
