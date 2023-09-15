import csv
import os
import time
import threading
import queue

from tkinter import ttk
from tkinter import *

import numpy as np
import pandas as pd

class ProcessData():
    def read_data(self, folder_path, read_pb, window):
        dfs = []
        file_names = sorted(os.listdir(folder_path))
        header = None

        num_files = 0
        counter = 0

        #Get number of files (only .txt)
        for file in file_names:
            if file.endswith('.txt'):
                num_files+=1

        increment = 100/num_files

        label = Label(window, text="Reading: ", font=("Helvetica", 16)) 
        label.place(x=120, y=10)
        read_pb.place(x=120, y=40, width=200)

        for file in file_names:
            if file.endswith('.txt'):
                print(f'Processing: {file}')
                file_path = os.path.join(folder_path, file)
                counter += 1

                if (counter < num_files):
                    read_pb['value'] += increment
                    window.update()
                else:
                    read_pb['value'] = 99.9 #if pb goes to 100 it resets?
                    window.update()

                if header is None:
                    df = pd.read_csv(file_path)
                    header = df.columns.tolist()
                else:
                    df = pd.read_csv(file_path, header=None, names=header)
                dfs.append(df)

        read_pb.place_forget()  
        label.place_forget()
        combined_df = pd.concat(dfs, ignore_index=True)
        return combined_df
    
    def clean_data(self, df, df_queue):

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

        # Calculate the initial start date.
        initial_datetime = datetime_obj - pd.Timedelta(seconds=seconds_at_first_valid_date-1) # Minus 1 because this is the next second (we want the previous so it matches the date above)

        # Convert from GMT to GMT+8. (AWST)
        initial_datetime =  initial_datetime + pd.Timedelta(hours=8)

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

        df_queue.put(df)

    def start_clean_data(self, clean_pb, window, df):
        df_queue = queue.Queue()

        label = Label(window, text="Cleaning: ", font=("Helvetica", 16)) 
        label.place(x=120, y=10)        
        clean_pb.place(x=120, y=40, width=200)

        clean_pb.start()

        thread = threading.Thread(target=ProcessData.clean_data, args=(self, df, df_queue))
        thread.start()

        while thread.is_alive():
            window.update()
    
        result_from_thread = df_queue.get()

        time.sleep(0.5)
        clean_pb.destroy()
        label.destroy()

        return result_from_thread

    def save_to_csv(self, df, file_name):
        df.to_csv(file_name, index=False)

    def start_save_to_csv(self, cleaned_data, path, write_pb, window):

        label = Label(window, text="Writing to CSV: ", font=("Helvetica", 16)) 
        label.place(x=120, y=10)        
        write_pb.place(x=120, y=40, width=200)

        write_pb.start()

        thread = threading.Thread(target=ProcessData.save_to_csv, args=(self, cleaned_data, path))
        thread.start()

        while thread.is_alive():
            window.update()

        time.sleep(0.5)
        write_pb.destroy()
        label.destroy()





    
