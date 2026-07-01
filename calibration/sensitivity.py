import pandas as pd 
import numpy as np

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

