import pandas as pd
from dataclasses import dataclass, field

from input_output import read_input_yaml, data_formatter, df_acc_ar
from processing import df_avg_acc, df_avg_ar
from calibration import expected_acc_values, expected_ar_values, sensitivity_calc

@dataclass
class DataInformation:
    sheet_name: str
    sheet_index: list

    df_original: dict = field(default_factor=dict)
    df_cleaned: dict = field(default_factor=dict)
    df_formatted: dict = field(default_factor=dict)

    df_acc: dict = field(default_factor=dict)
    df_ar: dict = field(default_factor=dict)
    
    df_avg_acc: dict = field(default_factor=dict)
    df_avg_ar: dict = field(default_factor=dict)

def main_logic():
    config = read_input_yaml(r"Input.yaml")
    file = config.path.logger

    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)

    logger_sheet_index = [2, 3, 4, 5, 6, 7, 8, 9]
    reference_sheet_index = [10, 11, 12, 13, 14, 15, 16, 17]
    num_sheets = len(logger_sheet_index)

    logger = DataInformation(logger_sheet_index, "logger")
    reference = DataInformation(reference_sheet_index, "reference")

    data_formatter(file, logger, reference, num_sheets)

    logger.df_acc, logger.df_ar = df_acc_ar(num_sheets, logger.sheet_index, logger.df_formatted)
    reference.df_acc, reference.df_ar = df_acc_ar(num_sheets, reference.sheet_index, reference.df_formatted)

    logger.df_avg_acc = df_avg_acc(num_sheets, logger.sheet_index, logger.df_acc)
    expected_acc = expected_acc_values(logger.df_avg_acc)
    print(sensitivity_calc(expected_acc, logger.df_avg_acc))

    logger.df_avg_ar = df_avg_ar(num_sheets, logger.sheet_index, logger.df_ar, mode = "logger", threshold=0.2)
    reference.df_avg_ar = df_avg_ar(num_sheets, reference.sheet_index, reference.df_ar, mode = "reference", threshold=200)
    expected_ar = expected_ar_values(logger.df_avg_ar, reference.df_avg_ar)
    print(sensitivity_calc(expected_ar, logger.df_avg_ar))

    #print(logger.df_avg_acc)
    #print(logger.df_avg_ar)
    #print(reference.df_avg_ar)
    #print(expected_ar)