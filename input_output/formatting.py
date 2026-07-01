import pandas as pd 
from .reader import read_xlsx
from .cleaning import df_clean, acc_df, ar_df

def data_formatter(file, logger, reference, num_sheets):
    logger.df_original = read_xlsx(file, logger.sheet_index)
    reference.df_original = read_xlsx(file, reference.sheet_index)

    logger.df_cleaned = df_clean(num_sheets, logger.sheet_index, logger.df_original)
    reference.df_cleaned = df_clean(num_sheets, reference.sheet_index, reference.df_original)

    logger.df_formatted, reference.df_formatted = format_df_time(logger, reference, num_sheets) # This should be improved as now you have many functions inside the time_format function, should be homogeneous

def format_df_time(logger, reference, num_sheets):
#START TIME FOR LOGGER LOOP and FORMAT LOGGER LOOP
    start_time_logger_array = []
    df_logger_formatted = {}

    for i in range(num_sheets):
        key = logger.sheet_index[i]
        values = logger.df_cleaned[key]

        start_time_logger = extract_start_logger(values)
        start_time_logger_array.append(start_time_logger)
        df_logger_added_time = add_time_logger(values)
        df_logger_formatted[key] = df_logger_added_time

#ADDING TIME TO REFERENCE DF
    df_reference_formatted = {}

    for i in range(num_sheets):
        key = reference.sheet_index[i]

        df_reference_added_time = add_time_reference(reference.df_cleaned[key], start_time_logger_array[i])
        df_reference_formatted[key] = df_reference_added_time #Can change so to add to reference_clean instead of making new format one
    return (df_logger_formatted, df_reference_formatted)

def extract_start_logger(df):
    td = pd.to_timedelta(df.iloc[0,0])
    #time_ms = int(td.total_seconds()*1000) -1 #Minus 1 because of rounding error when parsing
    #time_ms = (td.dt.total_seconds() * 1000).astype(int)
    time_ms = int(td.total_seconds() * 1000)
    return time_ms

def add_time_reference(df, start_time_logger_array):
    df = df.copy()
    #df["Time (formatted)"] = df["Time"] + start_time_logger_array
    df["Time (formatted)"] = df["Time"] + start_time_logger_array
    #print(start_time_logger_array)
    df_reordered = df.loc[:,['Time (formatted)', 'AccX', 'AccY', 'AccZ', 'ARXY', 'ARZ']]
    return(df_reordered)

def add_time_logger(df):
    df = df.copy()
    td = pd.to_timedelta(df.iloc[:, 0])
    time_ms = (td.dt.total_seconds() * 1000)
    df['Time (formatted)'] = time_ms
    df_reordered = df.loc[:,['Time (formatted)', 'AccX', 'AccY', 'AccZ', 'ArX', 'ArY']] #This, along with the same func in calc, should have the names in a variable
    return(df_reordered)

def df_acc_ar(num_sheets, sheet_index, df):
    df_acc = {}
    df_ar = {}
    for i in range(num_sheets):
        key = sheet_index[i]
        values = df[key]

        df_acc[key] = acc_df(values)
        df_ar[key] = ar_df(values)

        cols = df_ar[key].columns.drop("Time (formatted)")
        df_ar[key][cols] = df_ar[key][cols].apply(
            pd.to_numeric,
            errors="coerce"
        )

    return(df_acc, df_ar)
