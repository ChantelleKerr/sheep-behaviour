import csv
import os

import numpy as np
import pandas as pd


class ProcessData():
    def read_data(self, folder_path):
        """
        We need to change this function it currently deletes any rows after it finds the header in the first 
        """
        dfs = []
        file_names = sorted(os.listdir(folder_path))
        header = None  # Initialize header to None

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
        

        print("First Date:",datetime_obj)

        # Find the current overall second at the date and time above
        index_of_first_valid_row = first_valid_row.name
        seconds_at_first_valid_date = df.iloc[index_of_first_valid_row + 1]['ACCEL_X']
        seconds_at_first_valid_date = int(seconds_at_first_valid_date.replace('*', ''))
        print("Current Second:", seconds_at_first_valid_date - 1) # Minus 1 because this is the next second (we want the previous so it matches the date above)

        # Calculate the initial start date
        initial_datetime = datetime_obj - pd.Timedelta(seconds=seconds_at_first_valid_date)
        print("INITIAL DATE:", initial_datetime)

        df = df.drop(columns=['LAT', 'LON', 'DAY', 'MONTH', 'YEAR', 'HOUR', 'MINUTE', 'SECOND'])
        
        # Calculate datetime
        date_column = np.empty(len(df), dtype=object)
        current_datetime = initial_datetime
        for index, row in df.iterrows():
            date_column[index] = current_datetime.strftime('%d/%m/%Y %H:%M:%S')
            
            if row["ACCEL_X"].startswith("*") and index != 0:
                current_datetime += pd.Timedelta(seconds=1)

        # Assign the date_column to the DataFrame
        df['DATE'] = date_column

        # Remove rows starting with "*"
        mask = df.iloc[:, 0].str.startswith('*') 
        df = df[~mask]

        return df
        
    def save_to_csv(self, df, file_name):
        df.to_csv(file_name, index=False)





    
