import pandas as pd 

#def df_compare(df):
    

#Returns the average of all the columns in a df
def df_average(df):
    #average_df = df.mean(axis=0)
    average_df = df.select_dtypes(include="number").mean(axis=0)
    average_df = average_df.to_frame().T
    return(average_df)

#returns the standard deviation of all the columns in a df
def df_SD(df):
    SD_df = df.std()
    SD_df = SD_df.to_frame().T
    return(SD_df)

def expected_acc_values(df_logger_avg):
    df_logger_avg_acc = df_logger_avg.drop(["ArX", "ArY"], axis=1)
    df_expected_acc = pd.DataFrame(index=df_logger_avg_acc.index, columns = df_logger_avg_acc.columns)
    
    downwards_volts = 3
    orthogonal_volts = 2
    upwards_volts = 1

    downwards_g = 1
    orthogonal_g = 0
    upwards_g = -1

    buffer = 0.2
    
    for i in range(df_logger_avg_acc.shape[0]):
        for j in range(df_logger_avg_acc.shape[1]):
            if df_logger_avg_acc.iloc[i,j] >= downwards_volts - buffer and df_logger_avg_acc.iloc[i,j] <= downwards_volts + buffer:
                df_expected_acc.iloc[i,j] = downwards_g    

            elif df_logger_avg_acc.iloc[i,j] >= orthogonal_volts - buffer and df_logger_avg_acc.iloc[i,j] <= orthogonal_volts + buffer:
                df_expected_acc.iloc[i,j] = orthogonal_g    

            elif df_logger_avg_acc.iloc[i,j] >= upwards_volts - buffer and df_logger_avg_acc.iloc[i,j] <= upwards_volts + buffer:
                df_expected_acc.iloc[i,j] = upwards_g
  
            else:
                print("Out of range")

    return(df_expected_acc)



