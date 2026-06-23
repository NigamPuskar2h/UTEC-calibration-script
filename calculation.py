import pandas as pd 
import numpy as np
from scipy.stats import linregress

#Returns the average of all the columns in a df
def df_average(df, n):
    #average_df = df.mean(axis=0)
    if n == None:
        average_df = df.select_dtypes(include="number").mean(axis=0)
    elif n != None:
        average_df = df.iloc[:n].select_dtypes(include="number").mean(axis=0)
    average_df = average_df.to_frame().T
    return(average_df)

#returns the standard deviation of all the columns in a df
def df_SD(df):
    SD_df = df.std()
    SD_df = SD_df.to_frame().T
    return(SD_df)

def add_time_reference(df, start_time_logger_array):
    df = df.copy()
    df["Time (formatted)"] = df["Time"] + start_time_logger_array
    df_reordered = df.loc[:,['Time (formatted)', 'AccX', 'AccY', 'AccZ', 'ARXY', 'ARZ']]
    return(df_reordered)

def add_time_logger(df):
    df = df.copy()
    td = pd.to_timedelta(df.iloc[:, 0])
    time_ms = (td.dt.total_seconds() * 1000) - 1
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

    return(df_expected_acc, df_logger_avg_acc)

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

def step_detection(df):
    #df = pd.DataFrame({"A": [0, 1, 2, 3, 4, 5, 6, 7, 8]})
    smoothed_signal = rolling_average(df)
    gradient = df.diff()
    return gradient

def rolling_average(df):
    rolling_average = df.rolling(5,center=True, closed='both').sum()
    return rolling_average