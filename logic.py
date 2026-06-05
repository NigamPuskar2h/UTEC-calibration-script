import input_reader
import calculation
import pandas as pd

def main_logic():
    config = input_reader.read_input_yaml(r"Input.yaml")
    file = config.path.logger
    logger_sheet_index = [2,3,4,5,6,7,8,9]
    reference_sheet_index = [10, 11, 12, 13, 14, 15, 16, 17]
    df_logger_original = input_reader.read_xlsx(file, logger_sheet_index)
    
    #-------------------------
    #logger data
    df_logger_cleaned = {}
    df_logger_acc = {}
    df_logger_ar = {}
    logger_avg_acc = []

    # clean and average
    for i in range(len((logger_sheet_index))):
        key = logger_sheet_index[i]
        values = df_logger_original[key]
        cleaned = input_reader.clean_df(values)

        df_logger_cleaned[key] = cleaned
        df_logger_acc[key] = input_reader.acc_df(cleaned)
        df_logger_ar[key] = input_reader.ar_df(cleaned)

        logger_avg_acc.append(calculation.df_average(df_logger_acc[key], 20))

    df_logger_avg_acc = pd.concat(logger_avg_acc)
    #---------------------------



    df_expected_acc, df_logger_avg_acc = calculation.expected_acc_values(df_logger_avg_acc)
    x_sens, x_offs, y_sens, y_offs, z_sens, z_offs = calculation.sensitivity_calc(df_expected_acc, df_logger_avg_acc)
    #print(x_sens, y_sens , z_sens, x_offs, y_offs, z_offs)
