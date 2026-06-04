import input_reader
import calculation
import pandas as pd

def main_logic():
    config = input_reader.read_input_yaml(r"Input.yaml")
    file = config.path.logger
    sheet_index = [2,3,4,5,6,7,8,9]
    df_logger_original = input_reader.read_xlsx(file, sheet_index)
    
    #-------------------------
    df_logger_cleaned = {}
    df_logger_acc = {}
    df_logger_ar = {}
    logger_avg = []
    keys = list(df_logger_original.keys())

    # clean and average
    for i in range(len((sheet_index))):
        key = keys[i]
        values = df_logger_original[key]
        cleaned = input_reader.clean_df(values)

        df_logger_cleaned[key] = cleaned
        df_logger_acc[key] = input_reader.acc_df(cleaned)
        df_logger_ar[key] = input_reader.ar_df(cleaned)
        logger_avg.append(calculation.df_average(cleaned))

    df_logger_avg = pd.concat(logger_avg)
    
    #---------------------------

    df_expected_acc, df_logger_avg_acc = calculation.expected_acc_values(df_logger_avg)

    x_sens, x_offs, y_sens, y_offs, z_sens, z_offs = calculation.sensitivity_calc(df_expected_acc, df_logger_avg_acc)

    print(x_sens, y_sens , z_sens, x_offs, y_offs, z_offs)

    #print(df_logger_avg)
    #print(df_expected_acc)    