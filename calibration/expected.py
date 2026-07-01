import pandas as pd 
import numpy as np

def expected_acc_values(logger_acc):
    df_expected_acc = pd.DataFrame(index=logger_acc.index, columns = logger_acc.columns)
    
    downwards_volts = 3
    orthogonal_volts = 2
    upwards_volts = 1

    downwards_g = 1
    orthogonal_g = 0
    upwards_g = -1

    buffer = 0.2
    
    #Think this also loops through the data values, needs changing so it ignores the first column
    for i in range(logger_acc.shape[0]):
        for j in range(logger_acc.shape[1]):
            if logger_acc.iloc[i,j] >= (downwards_volts - buffer) and logger_acc.iloc[i,j] <= (downwards_volts + buffer):
                df_expected_acc.iloc[i,j] = downwards_g    

            elif logger_acc.iloc[i,j] >= (orthogonal_volts) - buffer and logger_acc.iloc[i,j] <= (orthogonal_volts + buffer):
                df_expected_acc.iloc[i,j] = orthogonal_g    

            elif logger_acc.iloc[i,j] >= (upwards_volts - buffer) and logger_acc.iloc[i,j] <= (upwards_volts + buffer):
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
