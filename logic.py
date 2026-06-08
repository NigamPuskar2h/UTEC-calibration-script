import input_reader
import calculation
import pandas as pd

def main_logic():
    config = input_reader.read_input_yaml(r"Input.yaml")
    file = config.path.logger

    logger_sheet_index = [2,3,4,5,6,7,8,9]
    reference_sheet_index = [10, 11, 12, 13, 14, 15, 16, 17]

    num_sheets = len(logger_sheet_index)
    df_logger_original = input_reader.read_xlsx(file, logger_sheet_index)
    df_reference_original = input_reader.read_xlsx(file, reference_sheet_index)
    
    df_logger_cleaned, df_logger_acc, df_logger_ar = df_format(num_sheets, logger_sheet_index, df_logger_original)
    df_reference_cleaned, df_reference_acc, df_reference_ar = df_format(num_sheets, reference_sheet_index, df_reference_original)

    logger_avg_acc = []
    for i in range(num_sheets):
        key = logger_sheet_index[i]
        logger_avg_acc.append(calculation.df_average(df_logger_acc[key], 20))

    df_logger_avg_acc = pd.concat(logger_avg_acc)
    df_expected_acc, df_logger_avg_acc = calculation.expected_acc_values(df_logger_avg_acc)
    x_sens, x_offs, y_sens, y_offs, z_sens, z_offs = calculation.sensitivity_calc(df_expected_acc, df_logger_avg_acc)
    #print(df_logger_acc)
    print(df_reference_acc)
    #print(x_sens, y_sens , z_sens, x_offs, y_offs, z_offs)
    '''
    #-------------------------
    #logger data
    df_logger_cleaned = {}
    df_logger_acc = {}
    df_logger_ar = {}
    logger_avg_acc = []
    start_time_logger_array = []
    # clean and average
    for i in range(num_sheets):
        key = logger_sheet_index[i]
        values = df_logger_original[key]
        cleaned = input_reader.clean_df(values)

        df_logger_cleaned[key] = cleaned
        df_logger_acc[key] = input_reader.acc_df(cleaned)
        df_logger_ar[key] = input_reader.ar_df(cleaned)


        logger_avg_acc.append(calculation.df_average(df_logger_acc[key], 20))

        start_time_logger = input_reader.extract_start_logger(cleaned)

        #start_time_logger_array.append(start_time_logger)
    '''
    #df_logger_avg_acc = pd.concat(logger_avg_acc)
    #---------------------------

    #print(start_time_logger_array[3])
    

    #df_expected_acc, df_logger_avg_acc = calculation.expected_acc_values(df_logger_avg_acc)
    #x_sens, x_offs, y_sens, y_offs, z_sens, z_offs = calculation.sensitivity_calc(df_expected_acc, df_logger_avg_acc)
    #print(x_sens, y_sens , z_sens, x_offs, y_offs, z_offs)
    #print(df_reference_original)

def df_format(num_sheets, sheet_index, df):
    #logger data
    df_cleaned = {}
    df_acc = {}
    df_ar = {}
    #logger_avg_acc = []
    #start_time_logger_array = []
    for i in range(num_sheets):
        key = sheet_index[i]
        values = df[key]
        cleaned = input_reader.clean_df(values)

        df_cleaned[key] = cleaned
        df_acc[key] = input_reader.acc_df(cleaned)
        df_ar[key] = input_reader.ar_df(cleaned)
    
    return(df_cleaned, df_acc, df_ar)


        #logger_avg_acc.append(calculation.df_average(df_logger_acc[key], 20))

        #start_time_logger = input_reader.extract_start_logger(cleaned)

        #start_time_logger_array.append(start_time_logger)