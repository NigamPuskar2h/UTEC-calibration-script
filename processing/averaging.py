import pandas as pd 
import numpy as np
from .step_detection import build_steps

def df_average(df, start, end):
    average_df = df.loc[start:end].select_dtypes(include="number").mean(axis=0).to_frame().T
    return(average_df)

def df_SD(df):
    SD_df = df.std()
    SD_df = SD_df.to_frame().T
    return(SD_df)

def df_avg_acc(num_sheets, sheet_index, df_acc):
    all_avg = []
    start = 0
    end = 20 #need to verify this
    for i in range(num_sheets):
        key = sheet_index[i]
        all_avg.append(df_average(df_acc[key], start, end))

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
                df_average(
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
