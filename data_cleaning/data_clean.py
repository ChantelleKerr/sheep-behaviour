import csv
import os

import numpy as np
import pandas as pd


class ProcessData():
    def read_data(self, folder_path):
        dfs = []
        file_names = sorted(os.listdir(folder_path))
        header = None

        for file in file_names:
            print(f'Processing: {file}')
            if file.endswith('.txt'):
                file_path = os.path.join(folder_path, file)

                if header is None:
                    df = pd.read_csv(file_path)
                    header = df.columns.tolist()
                else:
                    df = pd.read_csv(file_path, header=None, names=header)
                dfs.append(df)
                
        combined_df = pd.concat(dfs, ignore_index=True)
        return combined_df
    
    
    def clean_data(self, df):
        # Find the first row with no NaN values (This is where the first date and time is recorded)
        first_valid_row = df.dropna().iloc[0]

        # Extract the date values and format it for calculations
        columns_to_extract = ['DAY', 'MONTH', 'YEAR', 'HOUR', 'MINUTE', 'SECOND']
        values_of_first_valid_row = first_valid_row[columns_to_extract].astype(int).values
        datetime_format = '%d %m %Y %H %M %S'
        datetime_str = ' '.join(map(str, values_of_first_valid_row))
        datetime_obj = pd.to_datetime(datetime_str, format=datetime_format)

        # Find the current overall second at the date and time above
        index_of_first_valid_row = first_valid_row.name
        seconds_at_first_valid_date = df.iloc[index_of_first_valid_row + 1]['ACCEL_X']
        seconds_at_first_valid_date = int(seconds_at_first_valid_date.replace('*', ''))

        # Calculate the initial start date
        initial_datetime = datetime_obj - pd.Timedelta(seconds=seconds_at_first_valid_date-1) # Minus 1 because this is the next second (we want the previous so it matches the date above)
        
        df = df.drop(columns=['LAT', 'LON', 'DAY', 'MONTH', 'YEAR', 'HOUR', 'MINUTE', 'SECOND'])
        
        
        mask = np.logical_and([s.startswith('*') for s in df['ACCEL_X']], df.index % 1560 == 0)
        
        # Calculates how many minutes since the initial date (based on the mask)
        seconds_to_add = np.zeros(len(df))
        seconds_to_add[mask] = np.arange(0, mask.sum()) * 60
        
        # Calculates a new date from the initial date for every minute
        df['DATE'] = None
        df.loc[mask, 'DATE'] = initial_datetime + pd.to_timedelta(seconds_to_add[mask], unit='s')
        df['DATE'] = df['DATE'].shift(1)

        # Remove -2048,-2048,-2048 and shift the date one index before removing
        mask = (df['ACCEL_X'] == '-2048') & (df['ACCEL_Y'] == -2048) & (df['ACCEL_Z'] == -2048)
        mask_indices = df.index[mask]
        if not mask_indices.empty:
            next_index = mask_indices + 1
            df.loc[next_index, 'DATE'] = df.loc[mask_indices, 'DATE'].values
        
        # Remove rows starting with "*"
        mask2 = df.iloc[:, 0].str.startswith('*') 
        # Remove 0,0,0 rows
        mask3 = (df['ACCEL_X'] == '0') & (df['ACCEL_Y'] == 0) & (df['ACCEL_Z'] == 0)

        combined_mask = mask | mask2 | mask3
        df = df[~combined_mask]

        return df
        
    def save_to_csv(self, df, file_name):
        df.to_csv(file_name, index=False)





    
