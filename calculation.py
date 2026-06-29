import pandas as pd 
import numpy as np
from scipy.stats import linregress
'''
#Returns the average of all the columns in a df
def df_average(df, n):
    #average_df = df.mean(axis=0)
    if n == None:
        average_df = df.select_dtypes(include="number").mean(axis=0)
    elif n != None:
        average_df = df.iloc[:n].select_dtypes(include="number").mean(axis=0)
    average_df = average_df.to_frame().T
    return(average_df)
'''
#Returns the average of all the columns in a df
def df_average(df, start, end):
    #average_df = df.mean(axis=0)
    average_df = df.loc[start:end].select_dtypes(include="number").mean(axis=0).to_frame().T
    return(average_df)

#returns the standard deviation of all the columns in a df
def df_SD(df):
    SD_df = df.std()
    SD_df = SD_df.to_frame().T
    return(SD_df)

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

def expected_acc_values(df_logger_avg_acc):
    df_expected_acc = pd.DataFrame(index=df_logger_avg_acc.index, columns = df_logger_avg_acc.columns)
    
    downwards_volts = 3
    orthogonal_volts = 2
    upwards_volts = 1

    downwards_g = 1
    orthogonal_g = 0
    upwards_g = -1

    buffer = 0.2
    
    #Think this also loops through the data values, needs changing so it ignores the first column
    for i in range(df_logger_avg_acc.shape[0]):
        for j in range(df_logger_avg_acc.shape[1]):
            if df_logger_avg_acc.iloc[i,j] >= (downwards_volts - buffer) and df_logger_avg_acc.iloc[i,j] <= (downwards_volts + buffer):
                df_expected_acc.iloc[i,j] = downwards_g    

            elif df_logger_avg_acc.iloc[i,j] >= (orthogonal_volts) - buffer and df_logger_avg_acc.iloc[i,j] <= (orthogonal_volts + buffer):
                df_expected_acc.iloc[i,j] = orthogonal_g    

            elif df_logger_avg_acc.iloc[i,j] >= (upwards_volts - buffer) and df_logger_avg_acc.iloc[i,j] <= (upwards_volts + buffer):
                df_expected_acc.iloc[i,j] = upwards_g
  
            else:
                print("Out of range")

    return(df_expected_acc)

def sensitivity_calc(df_expected_acc, df_logger_avg_acc):
    x1 = pd.to_numeric(df_expected_acc.iloc[:, 0])
    x2 = pd.to_numeric(df_logger_avg_acc.iloc[:, 0])

    y1 = pd.to_numeric(df_expected_acc.iloc[:, 1])
    y2 = pd.to_numeric(df_logger_avg_acc.iloc[:, 1])

    z1 = pd.to_numeric(df_expected_acc.iloc[:, 2])
    z2 = pd.to_numeric(df_logger_avg_acc.iloc[:, 2])

    x_sens_offs = np.polyfit(x2, x1, 1)
    y_sens_offs = np.polyfit(y2, y1, 1)
    z_sens_offs = np.polyfit(z2, z1, 1)

    x_sens = x_sens_offs[0]
    x_offs = -x_sens_offs[1]/x_sens

    y_sens = y_sens_offs[0]
    y_offs = -y_sens_offs[1]/y_sens

    z_sens = z_sens_offs[0]
    z_offs = -z_sens_offs[1]/z_sens

    return(x_sens, x_offs, y_sens, y_offs, z_sens, z_offs)

#GETS THE START AND POINTS FOR EACH MINI JUMPP. Next step is to use start and end points to get ranges, which you can then use to get the timess.
def step_detection(num_sheets, sheet_index, df, sheet_name, column_heading):    
    step_up = {}
    step_down = {}
    segments = {}
    step_times = {}
    start_padding = 1
    end_padding = 14

    if sheet_name == "logger":
        threshold = 0.2
    elif sheet_name == "reference":
        threshold = 200

    for i in range(num_sheets):
        key = sheet_index[i]
        values = df[key]

        values["gradient"] = gradient(values[column_heading]) #since the logger and reference have different titles, put it as 'or'

        step_up_temp = values.nlargest(20, "gradient")
        step_down_temp = values.nsmallest(20, "gradient")

        filtered_step_up = step_up_temp[step_up_temp['gradient'] > threshold].sort_values(by = ["Time (formatted)"])
        filtered_step_down = step_down_temp[step_down_temp['gradient'].abs() > threshold].sort_values(by = ["Time (formatted)"])

        step_up = turning_point(filtered_step_up, "up")[:4]
        step_down = turning_point(filtered_step_down, "down")[:4]

        segments[key] = []
        for u, d in zip(step_up, step_down):
            start = min(u, d) + start_padding
            end = max(u, d) - end_padding

            segments[key].append(
                values.loc[[start,end]]
            )
            #print(values.loc[[start, end], ["Time (formatted)"]])      
     
        for sheet, step_list in segments.items():
            step_times[sheet] = {}
            for step_num, data in enumerate(step_list, start=1):
                step_times[sheet][step_num] = data["Time (formatted)"].tolist() 
   
    return step_times
    #return segments
        
def turning_point(df, position):
    indices = df.index.to_series()

    if position == "up":
        return indices[indices.diff().abs().fillna(2) != 1].tolist()
    elif position == "down":
        return indices[indices.diff(periods=-1).abs().fillna(2) != 1].tolist()

def gradient(df):
    numeric = pd.to_numeric(df, errors = 'coerce')  #converts any non-numerical data to 0 difference
    smoothed_signal = numeric.rolling(window=4, center=True).median()   #These two should really be in the data filter function
    #smoothed_signal = rolling_average(numeric)
    gradient = smoothed_signal.diff().fillna(0)
    return gradient

def logger_step_detection(num_sheets, reference_sheet_index, logger_sheet_index, step_times, logger_df):

    logger_step_times = {}

    for i in range(num_sheets):

        ref_key = reference_sheet_index[i]
        logger_key = logger_sheet_index[i]

        values = logger_df[logger_key]

        logger_step_times[logger_key] = {}

        for step_num, (start_time, end_time) in step_times[ref_key].items():

            start_idx = ((values["Time (formatted)"] - start_time).abs().idxmin())

            end_idx = ((values["Time (formatted)"] - end_time).abs().idxmin())

            logger_step_times[logger_key][step_num] = (start_idx, end_idx)
            #print(start_time, end_time)
            #print(start_idx, end_idx)
    return logger_step_times
    #return