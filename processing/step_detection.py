import pandas as pd 
import numpy as np

def build_steps(values, mode, threshold):

    if mode == "logger":
        ArX_steps = detect_steps(values, "ArX", threshold)
        ArY_steps = detect_steps(values, "ArY", threshold)

        combined = ArX_steps + ArY_steps

    elif mode == "reference":
        ArZ_steps = detect_steps(values, "ARZ", threshold)
        combined = ArZ_steps

    else:
        raise ValueError("Unknown mode")
    
    combined.sort(key=lambda s: s["start_time"])
    return combined

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
'''
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

'''