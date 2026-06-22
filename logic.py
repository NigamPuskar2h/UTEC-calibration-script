import input_reader
import calculation
import pandas as pd

def main_logic():
    config = input_reader.read_input_yaml(r"Input.yaml")
    file = config.path.logger

    logger_sheet_index = [2, 3, 4, 5, 6, 7, 8, 9]
    reference_sheet_index = [10, 11, 12, 13, 14, 15, 16, 17]

    num_sheets = len(logger_sheet_index)
    df_logger_original = input_reader.read_xlsx(file, logger_sheet_index)
    df_reference_original = input_reader.read_xlsx(file, reference_sheet_index)

    df_logger_cleaned = df_clean(num_sheets, logger_sheet_index, df_logger_original)
    df_reference_cleaned = df_clean(num_sheets, reference_sheet_index, df_reference_original)

#------------------------------------------
#START TIME FOR REFERENCE LOOP
    start_time_logger_array = []
    #for i, key in enumerate(logger_sheet_index):
    for i in range(num_sheets):
        key = logger_sheet_index[i]
        values = df_logger_cleaned[key]
        #logger_avg_acc.append(calculation.df_average(df_logger_acc[key], 20))
        start_time_logger = input_reader.extract_start_logger(values)
        start_time_logger_array.append(start_time_logger)
    print(start_time_logger_array)
#------------------------------------------
    
#------------------------------------------
#ADDING TIME TO REFERENCE DF
    df_reference_formatted = {}
    for i in range(num_sheets):
        key = reference_sheet_index[i]
        #values = df
        df_added_time = calculation.add_time(df_reference_original[key], start_time_logger_array[i])
        df_reference_formatted[key] = df_added_time #Can change so to add to reference_clean instead of making new format one
#------------------------------------------

    df_logger_acc, df_logger_ar = df_acc_ar(num_sheets, logger_sheet_index, df_logger_original)
    df_reference_acc, df_reference_ar = df_acc_ar(num_sheets, reference_sheet_index, df_reference_formatted)

    print(df_logger_cleaned)
#------------------------------------------
#AVERAGE LOOP
    logger_avg_acc = []
    num_values = 20 #need to verify this
    for i in range(num_sheets):
        key = logger_sheet_index[i]
        logger_avg_acc.append(calculation.df_average(df_logger_acc[key], num_values))
    df_logger_avg_acc = pd.concat(logger_avg_acc)
#------------------------------------------


    df_expected_acc, df_logger_avg_acc = calculation.expected_acc_values(df_logger_avg_acc)
    x_sens, x_offs, y_sens, y_offs, z_sens, z_offs = calculation.sensitivity_calc(df_expected_acc, df_logger_avg_acc)
    #print(x_sens, y_sens , z_sens, x_offs, y_offs, z_offs)

def df_clean(num_sheets, sheet_index, df):
    df_cleaned = {}
    for i in range(num_sheets):
        key = sheet_index[i]
        values = df[key]
        cleaned = input_reader.clean_df(values)
        df_cleaned[key] = cleaned
    return(df_cleaned)

def df_acc_ar(num_sheets, sheet_index, df_cleaned):
    df_acc = {}
    df_ar = {}
    for i in range(num_sheets):
        key = sheet_index[i]
        cleaned = df_cleaned[key]

        df_acc[key] = input_reader.acc_df(cleaned)
        df_ar[key] = input_reader.ar_df(cleaned)
    
    return(df_acc, df_ar)
