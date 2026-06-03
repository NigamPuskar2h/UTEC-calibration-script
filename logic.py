import input_reader
import calculation
import pandas as pd

def main_logic():
    config = input_reader.read_input_yaml(r"Input.yaml")
    file = config.path.logger
    sheet_index = [2,3,4,5,6,7,8,9]
    df_logger_original = input_reader.read_xlsx(file, sheet_index)
    
    logger_avg = []
    df_logger_cleaned = {}
    keys = list(df_logger_original.keys())

    for i in range(len((sheet_index))):
        key = keys[i]
        values = df_logger_original[key]

        df_logger_cleaned[key] = input_reader.clean_df(values)
        logger_avg.append(calculation.df_average(values))

    df_logger_avg = pd.concat(logger_avg)

    df_expected_acc = calculation.expected_acc_values(df_logger_avg)
    print(df_logger_avg)
    print(df_expected_acc)    