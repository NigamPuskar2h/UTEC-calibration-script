import input_reader
import calculation
import pandas as pd

def main_logic():
    config = input_reader.read_input_yaml(r"Input.yaml")
    file = config.path.logger
    sheet_index = [2,3,4,5,6,7,8,9]
    df_dict_original = input_reader.read_xlsx(file, sheet_index)
    #df = input_reader.clean_df(df)


    results = []
    df_dict_cleaned = {}
    keys = list(df_dict_original.keys())

    for i in range(len((sheet_index))):
        key = keys[i]
        values = df_dict_original[key]

        df_dict_cleaned[key] = input_reader.clean_df(values)

        results.append(calculation.df_average(values))

    res_df = pd.concat(results)
    print(df_dict_original)
    print(df_dict_cleaned)
    print(res_df)
