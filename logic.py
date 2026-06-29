import input_reader
import calculation
import pandas as pd
from dataclasses import dataclass

@dataclass
class data_information:
    def __init__(self, sheet_index, name):
        self.sheet_name = name
        self.sheet_index = sheet_index
        self.df_original = dict
        self.df_cleaned = dict
        self.df_formatted = dict
        self.df_acc = dict
        self.df_ar = dict

def data_formatter(file, logger, reference, num_sheets):
    logger.df_original = input_reader.read_xlsx(file, logger.sheet_index)
    reference.df_original = input_reader.read_xlsx(file, reference.sheet_index)

    logger.df_cleaned = df_clean(num_sheets, logger.sheet_index, logger.df_original)
    reference.df_cleaned = df_clean(num_sheets, reference.sheet_index, reference.df_original)

    logger.df_formatted, reference.df_formatted = format_df_time(logger, reference, num_sheets) # This should be improved as now you have many functions inside the time_format function, should be homogeneous
    

def main_logic():
    config = input_reader.read_input_yaml(r"Input.yaml")
    file = config.path.logger

    logger_sheet_index = [2, 3, 4, 5, 6, 7, 8, 9]
    reference_sheet_index = [10, 11, 12, 13, 14, 15, 16, 17]

    logger = data_information(logger_sheet_index, "logger")
    reference = data_information(reference_sheet_index, "reference")

    num_sheets = len(logger_sheet_index)

    data_formatter(file, logger, reference, num_sheets)

    logger.df_acc, logger.df_ar = df_acc_ar(num_sheets, logger.sheet_index, logger.df_formatted)
    reference.df_acc, reference.df_ar = df_acc_ar(num_sheets, reference.sheet_index, reference.df_formatted)

    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)

    reference_step_times = calculation.step_detection(num_sheets, reference.sheet_index, reference.df_formatted, reference.sheet_name, "ARZ")
    #print(reference_step_times)
    logger_step_times = calculation.logger_step_detection(num_sheets, reference.sheet_index, logger.sheet_index, reference_step_times, logger.df_formatted)
    #print(logger_step_times)
    #print(logger.df_formatted[2]["Time (formatted)"])

    '''  
    for sheet, steps in logger_step_times.items():
        for step_num, data in steps.items():
            print(f"Sheet: {sheet}, Step: {step_num}")
            #print(logger.df_formatted[sheet, ])
            print(data)
    #print(logger.df_formatted[2].loc[:,"Time (formatted)"])
''' 
#------------------------------------------
#AVERAGE ACC LOOP
    logger_avg_acc = []
    start = 0
    num_values = 20 #need to verify this
    for i in range(num_sheets):
        key = logger_sheet_index[i]
        logger_avg_acc.append(calculation.df_average(logger.df_acc[key], start,  num_values))
    df_logger_avg_acc = pd.concat(logger_avg_acc)
    df_logger_avg_acc = df_logger_avg_acc.drop('Time (formatted)', axis=1)

    df_expected_acc = calculation.expected_acc_values(df_logger_avg_acc)
    x_sens, x_offs, y_sens, y_offs, z_sens, z_offs = calculation.sensitivity_calc(df_expected_acc, df_logger_avg_acc)
    print(x_sens, y_sens , z_sens, x_offs, y_offs, z_offs)
#------------------------------------------
#AVERAGE AR LOOP
    sheet = list(logger_step_times.keys())[4]
    logger_avg_ar = []
    for step_num, data in logger_step_times[sheet].items():
        #key = logger.sheet_index[sheet]
        print(f"Sheet: {sheet}, Step: {step_num}")
        #print(data)
        print(logger.df_formatted[sheet].loc[data[0]:data[1],:])
        logger_avg_ar.append(calculation.df_average(logger.df_formatted[sheet], data[0], data[1]))
    print(pd.concat(logger_avg_ar))

def df_clean(num_sheets, sheet_index, df):
    df_cleaned = {}
    for i in range(num_sheets):
        key = sheet_index[i]
        values = df[key]
        cleaned = input_reader.clean_df(values)
        df_cleaned[key] = cleaned
    return(df_cleaned)

def df_acc_ar(num_sheets, sheet_index, df):
    df_acc = {}
    df_ar = {}
    for i in range(num_sheets):
        key = sheet_index[i]
        values = df[key]

        df_acc[key] = input_reader.acc_df(values)
        df_ar[key] = input_reader.ar_df(values)
    
    return(df_acc, df_ar)

def format_df_time(logger, reference, num_sheets):
#START TIME FOR LOGGER LOOP and FORMAT LOGGER LOOP
    start_time_logger_array = []
    df_logger_formatted = {}

    for i in range(num_sheets):
        key = logger.sheet_index[i]
        values = logger.df_cleaned[key]

        start_time_logger = input_reader.extract_start_logger(values)
        start_time_logger_array.append(start_time_logger)
        #print(start_time_logger)
        df_logger_added_time = calculation.add_time_logger(values)
        df_logger_formatted[key] = df_logger_added_time

#ADDING TIME TO REFERENCE DF
    df_reference_formatted = {}

    for i in range(num_sheets):
        key = reference.sheet_index[i]

        df_reference_added_time = calculation.add_time_reference(reference.df_cleaned[key], start_time_logger_array[i])
        df_reference_formatted[key] = df_reference_added_time #Can change so to add to reference_clean instead of making new format one
    return (df_logger_formatted, df_reference_formatted)

