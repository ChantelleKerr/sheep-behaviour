import os
import re

import pandas as pd


def get_hertz_per_second(file_path):
    df = pd.read_csv(file_path)

    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')

    date_mask = df['DATE'].notna()
    minute_indices = date_mask[date_mask].index

    minute_counts = pd.Series(minute_indices).diff().fillna(minute_indices[0]).astype(int)

    hertz_per_second = minute_counts / 60

    average_hertz_per_second = hertz_per_second.mean()

    print("Average Hertz per Second:")
    print(average_hertz_per_second)
    return round(average_hertz_per_second, 1)
    
        
    #return df


def store_report(file_path, hertz):
    match = re.search(r'ACCEL_(\w+)', file_path)

    if match:
        sheep = match.group(1)

        data = {'Sheep': [sheep], 'Hertz': [hertz]}
        df = pd.DataFrame(data)

        output_file = 'ACCEL_Report.csv'
        df.to_csv(output_file, index=False)


# TODO: Convert to work with all cleaned files 
#       - Threading
#       - lock on output file (so data is not overwitten)

data_file = "test_data/cleaned_accel/ACCEL_GPS0028.csv"
hz = get_hertz_per_second(data_file)
store_report(data_file, hz)

