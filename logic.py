import input_reader
import calculation

def main_logic():
    config = input_reader.read_input_yaml(r"Input.yaml")
    file = config.path.logger
    df = input_reader.read_csv(file)
    logger_df = input_reader.parse_logger(df)
    logger_df = input_reader.clean_df(logger_df)
    average_df = calculation.df_average(logger_df)
    #SD_df = calculation.df_SD(logger_df)
    print(average_df)
