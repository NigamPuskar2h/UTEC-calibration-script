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
        self.df_avg_acc = dict
        self.df_avg_ar = dict

def main_logic():
    config = input_reader.read_input_yaml(r"Input.yaml")
    file = config.path.logger

    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)

    logger_sheet_index = [2, 3, 4, 5, 6, 7, 8, 9]
    reference_sheet_index = [10, 11, 12, 13, 14, 15, 16, 17]
    num_sheets = len(logger_sheet_index)

    logger = data_information(logger_sheet_index, "logger")
    reference = data_information(reference_sheet_index, "reference")

    data_formatter(file, logger, reference, num_sheets)

    logger.df_acc, logger.df_ar = df_acc_ar(num_sheets, logger.sheet_index, logger.df_formatted)
    reference.df_acc, reference.df_ar = df_acc_ar(num_sheets, reference.sheet_index, reference.df_formatted)

    logger.df_avg_acc = df_avg_acc(num_sheets, logger.sheet_index, logger.df_acc)
    expected_acc = calculation.expected_acc_values(logger.df_avg_acc)
    print(calculation.sensitivity_calc(expected_acc, logger.df_avg_acc))

    logger.df_avg_ar = df_avg_ar(num_sheets, logger.sheet_index, logger.df_ar, mode = "logger", threshold=0.2)
    reference.df_avg_ar = df_avg_ar(num_sheets, reference.sheet_index, reference.df_ar, mode = "reference", threshold=200)
    expected_ar = calculation.expected_ar_values(logger.df_avg_ar, reference.df_avg_ar)
    print(calculation.sensitivity_calc(expected_ar, logger.df_avg_ar))

    #print(logger.df_avg_acc)
    #print(logger.df_avg_ar)
    #print(reference.df_avg_ar)
    #print(expected_ar)

def data_formatter(file, logger, reference, num_sheets):
    logger.df_original = input_reader.read_xlsx(file, logger.sheet_index)
    reference.df_original = input_reader.read_xlsx(file, reference.sheet_index)

    logger.df_cleaned = df_clean(num_sheets, logger.sheet_index, logger.df_original)
    reference.df_cleaned = df_clean(num_sheets, reference.sheet_index, reference.df_original)

    logger.df_formatted, reference.df_formatted = format_df_time(logger, reference, num_sheets) # This should be improved as now you have many functions inside the time_format function, should be homogeneous

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

        cols = df_ar[key].columns.drop("Time (formatted)")
        df_ar[key][cols] = df_ar[key][cols].apply(
            pd.to_numeric,
            errors="coerce"
        )

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
        df_logger_added_time = calculation.add_time_logger(values)
        df_logger_formatted[key] = df_logger_added_time

#ADDING TIME TO REFERENCE DF
    df_reference_formatted = {}

    for i in range(num_sheets):
        key = reference.sheet_index[i]

        df_reference_added_time = calculation.add_time_reference(reference.df_cleaned[key], start_time_logger_array[i])
        df_reference_formatted[key] = df_reference_added_time #Can change so to add to reference_clean instead of making new format one
    return (df_logger_formatted, df_reference_formatted)

def build_steps(values, mode, threshold):

    if mode == "logger":
        ArX_steps = calculation.detect_steps(values, "ArX", threshold)
        ArY_steps = calculation.detect_steps(values, "ArY", threshold)

        combined = ArX_steps + ArY_steps

    elif mode == "reference":
        ArZ_steps = calculation.detect_steps(values, "ARZ", threshold)
        combined = ArZ_steps

    else:
        raise ValueError("Unknown mode")
    
    combined.sort(key=lambda s: s["start_time"])
    return combined

def df_avg_acc(num_sheets, sheet_index, df_acc):
    all_avg = []
    start = 0
    end = 20 #need to verify this
    for i in range(num_sheets):
        key = sheet_index[i]
        all_avg.append(calculation.df_average(df_acc[key], start, end))

    df_avg_acc = (
        pd.concat(all_avg)
        .drop(columns = "Time (formatted)")
    )
    return df_avg_acc

def df_avg_ar(num_sheets, sheet_index, df_ar, mode, threshold):
    all_steps = {}
    all_avg = []

    offset = 0.0539
    sensitivity = 3.99

    for i in range(num_sheets):
        key = sheet_index[i]
        values = df_ar[key] #Built the same as df.formatted, so just using df_ar

        steps = build_steps(values, mode, threshold)

        if len(steps) == 0:
            n = len(values)
            window = max(1, n // 8)

            steps = []
            for k in range(4):  # FORCE 4 outputs
                start = k * window
                end = min((k + 1) * window - 1, n - 1)

                steps.append({
                    "indices": (start, end),
                    "start_time": None,
                    "end_time": None
                })
            
        all_steps[key] = {
            step_num: {
                "indices": step["indices"],
                "start_time": step["start_time"],
                "end_time": step["end_time"]
            }
            for step_num, step in enumerate(steps, start=1)
        }     

        for step_num, data in all_steps[key].items():
            #print(f"sheet: {key}, step: {step_num}")
            #print("indices: ", data["indices"])
            #print("times: ", data["start_time"], data["end_time"])

            all_avg.append(
                calculation.df_average(
                    df_ar[key], 
                    data["indices"][0], 
                    data["indices"][1]
                )
            )

        df_avg_ar = (
            pd.concat(all_avg)
            .drop(columns = "Time (formatted)")
        )

        if mode == "reference":
            numeric_cols = df_avg_ar.columns
            df_avg_ar[numeric_cols] = (
                df_avg_ar[numeric_cols] / 1000 - offset
            ) * sensitivity

            df_avg_ar = df_avg_ar.drop(columns = "ARXY")
        elif mode == "logger":
            pass
        else:
            raise ValueError("Unknown mode")
    return df_avg_ar