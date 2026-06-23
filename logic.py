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

#------------------------------------------
#AVERAGE LOOP
    logger_avg_acc = []
    num_values = 20 #need to verify this
    for i in range(num_sheets):
        key = logger_sheet_index[i]
        logger_avg_acc.append(calculation.df_average(logger.df_acc[key], num_values))
    df_logger_avg_acc = pd.concat(logger_avg_acc)
#------------------------------------------
    #turning_points(num_sheets, logger.sheet_index, logger.df_formatted, logger.sheet_name)
    turning_points(num_sheets, reference.sheet_index, reference.df_formatted, reference.sheet_name, "ARZ")
    #print(reference.df_formatted)
'''
#------------------------------------------
#WORK OUT TURNING POINTS
    for i in range(num_sheets):
        key = logger_sheet_index[i]
        values = logger.df_formatted[key]

        values["gradient"] = calculation.step_detection(values['ArY'])
    #pd.set_option('display.max_rows', None)
    step_up = logger.df_formatted[2].nlargest(40, "gradient")
    step_down = logger.df_formatted[2].nsmallest(40, "gradient")
    threshold = 0.2
    filtered_df = step_up[step_up["gradient"] > threshold]
    print(filtered_df.sort_values(by = ["Time (formatted)"]))
'''

    #------------------------------------------
    #df_expected_acc, df_logger_avg_acc = calculation.expected_acc_values(df_logger_avg_acc)
    #x_sens, x_offs, y_sens, y_offs, z_sens, z_offs = calculation.sensitivity_calc(df_expected_acc, df_logger_avg_acc)
    #print(x_sens, y_sens , z_sens, x_offs, y_offs, z_offs)

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
    #for i, key in enumerate(logger_sheet_index):
    for i in range(num_sheets):
        key = logger.sheet_index[i]
        values = logger.df_cleaned[key]
        #logger_avg_acc.append(calculation.df_average(df_logger_acc[key], 20))
        start_time_logger = input_reader.extract_start_logger(values)
        start_time_logger_array.append(start_time_logger)
        
        df_logger_added_time = calculation.add_time_logger(values)
        df_logger_formatted[key] = df_logger_added_time

#ADDING TIME TO REFERENCE DF
    df_reference_formatted = {}
    for i in range(num_sheets):
        key = reference.sheet_index[i]
        #values = df
        df_reference_added_time = calculation.add_time_reference(reference.df_cleaned[key], start_time_logger_array[i])
        df_reference_formatted[key] = df_reference_added_time #Can change so to add to reference_clean instead of making new format one
    return (df_logger_formatted, df_reference_formatted)

def turning_points(num_sheets, sheet_index, df, sheet_name, column_heading):
    step_up = {}
    step_down = {}
    filtered_df = {}

    if sheet_name == "logger":
        threshold = 0.2
    elif sheet_name == "reference":
        threshold = 200

    for i in range(num_sheets):
        key = sheet_index[i]
        values = df[key]

        values["gradient"] = calculation.gradient(values[column_heading]) #since the logger and reference have different titles, put it as 'or'

        step_up[key] = values.nlargest(40, "gradient")
        step_down[key] = values.nsmallest(40, "gradient")

        filtered_df[key] = step_up[key][step_up[key]["gradient"] > threshold]
        print(filtered_df[key].sort_values(by = ["Time (formatted)"]))
