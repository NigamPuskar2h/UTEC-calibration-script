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