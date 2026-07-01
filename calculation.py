import pandas as pd 
import numpy as np
from scipy.stats import linregress
#Returns the average of all the columns in a df
def df_average(df, start, end):
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

def expected_ar_values(logger_ar, reference_ar):
    df_expected_acc = pd.DataFrame(
        np.zeros_like(logger_ar),
        index=logger_ar.index,
        columns=logger_ar.columns
    )

    slow_max = 2.6
    slow_min = 1.5
    neutral = 2.0
    fast_max = 3.8
    fast_min = 0.2

    buffer = 0.2

    for i in range(logger_ar.shape[0]):

        # pick active axis per row (same idea as calibration sheet)
        arx = logger_ar.iloc[i, 0]
        ary = logger_ar.iloc[i, 1]

        # decide which axis is "active" (farthest from neutral)
        if abs(arx - neutral) >= abs(ary - neutral):
            active_col = 0
            active_val = arx
        else:
            active_col = 1
            active_val = ary

        # classify bucket → sign
        if abs(active_val - slow_max) <= buffer:
            sign = -1
        elif abs(active_val - slow_min) <= buffer:
            sign = +1
        elif abs(active_val - fast_max) <= buffer:
            sign = -1
        elif abs(active_val - fast_min) <= buffer:
            sign = +1
        else:
            sign = 0

        # assign expected value (row-aligned reference!)
        expected_val = sign * abs(reference_ar.iloc[i])

        # fill output
        df_expected_acc.iloc[i, active_col] = expected_val
        df_expected_acc.iloc[i, 1 - active_col] = 0

    return df_expected_acc

def sensitivity_calc(df_expected, df_logger):
    sensitivities = []

    # ensure numeric + aligned
    df_expected = df_expected.apply(pd.to_numeric)
    df_logger = df_logger.apply(pd.to_numeric)

    n_cols = df_expected.shape[1]

    for col in range(n_cols):
        expected = df_expected.iloc[:, col]
        logger = df_logger.iloc[:, col]

        # linear fit: logger → expected
        slope, intercept = np.polyfit(logger, expected, 1)

        sens = float(slope)
        offset = float(-intercept / slope) if slope != 0 else np.nan

        sensitivities.append((sens, offset))

    return sensitivities

#GETS THE START AND POINTS FOR EACH MINI JUMPP. Next step is to use start and end points to get ranges, which you can then use to get the timess.
'''
def step_detection(num_sheets, sheet_index, df, sheet_name, column_heading):    
    step_up = {}
    step_down = {}
    segments = {}
    step_times = {}
    start_padding = 5
    end_padding = 5

    if sheet_name == "logger":
        threshold = 0.2
    elif sheet_name == "reference":
        threshold = 200

    for i in range(num_sheets):
        key = sheet_index[i]
        values = df[key]

        values["gradient"] = gradient(values[column_heading])

        step_up_temp = values.nlargest(20, "gradient")
        step_down_temp = values.nsmallest(20, "gradient")

        filtered_step_up = step_up_temp[step_up_temp['gradient'] > threshold].sort_values(by = ["Time (formatted)"])
        filtered_step_down = step_down_temp[step_down_temp['gradient'].abs() > threshold].sort_values(by = ["Time (formatted)"])

        step_up = turning_point(filtered_step_up, "up")[:4]
        step_down = turning_point(filtered_step_down, "down")[:4]

        segments[key] = []
        for u, d in zip(step_up, step_down):
            start = min(u, d)
            end = max(u, d)

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
 '''
def detect_steps(values, column, threshold):
    padding = 5
    values = values.copy()
    values["gradient"] = gradient(values[column])

    step_up_temp = values.nlargest(20, "gradient")
    step_down_temp = values.nsmallest(20, "gradient")

    #print(step_down_temp)

    filtered_up = step_up_temp[
        step_up_temp["gradient"] > threshold
    ].sort_values("Time (formatted)")

    filtered_down = step_down_temp[
        step_down_temp["gradient"].abs() > threshold
    ].sort_values("Time (formatted)")

    #print(filtered_down)

    step_up = turning_point(filtered_up, "up")
    step_down = turning_point(filtered_down, "down")

    min_separation = 20
    i = 0
    while i < min(len(step_up), len(step_down)):
        if abs(step_up[i] - step_down[i]) < min_separation:
            step_up.pop(i)
            step_down.pop(i)
        else:
            i += 1

    step_up = step_up[:4]
    step_down = step_down[:4]
       
    #print(step_down)
    
    segments = []
    for u, d in zip(step_up, step_down):
        start = min(u, d) + padding
        end = max(u, d) - padding

        segments.append({
            "indices": [start, end],
            "start_time": int(values.loc[start, "Time (formatted)"]),
            "end_time": int(values.loc[end, "Time (formatted)"])
        })
        #print(values.loc[[start, end], ["Time (formatted)"]])      
    return segments

def turning_point(df, position):
    indices = df.index.to_series()

    if position == "up":
        return indices[indices.diff().abs().fillna(2) != 1].tolist()
    elif position == "down":
        return indices[indices.diff(periods=-1).abs().fillna(2) != 1].tolist()

def gradient(df):
    numeric = pd.to_numeric(df, errors = 'coerce')  #converts any non-numerical data to 0 difference
    smoothed_signal = numeric.rolling(window=10, center=True).median()   #These two should really be in the data filter function
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