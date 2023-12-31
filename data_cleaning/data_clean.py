import csv
import os
import queue
import threading
import time
from tkinter import *
from tkinter import ttk
from datetime import datetime

import numpy as np
import pandas as pd
# import logging necessary file
from logger_config import get_logger, log_func_call
#init the logger
logger = get_logger(__name__)

class ProcessData():
    @log_func_call()
    def read_data(self, folder_path, df_queue):
        dfs = []
        file_names = sorted(os.listdir(folder_path))
        combined_df = []

        header = None
        found_day_15 = False
        day_counter = 0
        MAX_EXPERIMENT_DAYS = 34

        for idx, file in enumerate(file_names):
            # We only want to process 34 days worth of files
            if day_counter >= MAX_EXPERIMENT_DAYS:
                break
            
            if file.endswith('.txt'):
                print(f'Processing: {file}')
                logger.info(f'Processing: {file}') # process logging
                file_path = os.path.join(folder_path, file)
                if os.path.getsize(file_path) > 0:

                    if header is None:
                        df = pd.read_csv(file_path)
                        header = df.columns.tolist()
                        if header != ['ACCEL_X', 'ACCEL_Y', 'ACCEL_Z', 'LAT', 'LON', 'DAY', 'MONTH', 'YEAR', 'HOUR', 'MINUTE', 'SECOND']:
                            break
                    else:
                        df = pd.read_csv(file_path, header=None, names=header)
                    
                    rows_with_day_15 = df[df['DAY'] == 15]

                    if len(rows_with_day_15) > 0:
                        found_day_15 = True
                    
                    if found_day_15:
                        dfs.append(df)
                        day_counter += 1

        if not found_day_15:
            df_queue.put([])
            return []
        try:
            combined_df = pd.concat(dfs, ignore_index=True)
        except:
            print("Error: Not enough memory on disk or invalid files in directory")
            logger.error("Error: Not enough memory on disk or invalid files in directory __at class data_clean, read_data function")
        df_queue.put(combined_df)

    @log_func_call()
    def start_read_data(self, folder_path, window):
        df_queue = queue.Queue()
        label = Label(window, text="Reading: ", font=("Helvetica", 16)) 
        label.place(relx=.5, rely=.5, x=100, y=-30, anchor=CENTER)   
        read_pb = ttk.Progressbar(window, mode="indeterminate", style="TProgressbar")
        read_pb.place(relx=.5, rely=.5, x=100, anchor=CENTER, width=200)

        read_pb.start()

        thread = threading.Thread(target=ProcessData.read_data, args=(self, folder_path, df_queue))
        thread.start()

        while thread.is_alive():
            window.update()

        result_from_thread = df_queue.get()

        time.sleep(0.5)
        read_pb.destroy()  
        label.destroy()

        return result_from_thread
    
    @log_func_call()
    def clean_data(self, df, df_queue):

        try:
            first_index_of_day_15 = df[df['DAY'] == 15].index.min()
            # Remove all rows before that index and reset the index
            df = df.iloc[first_index_of_day_15:].reset_index(drop=True)

            # Extract the date values and format it for calculations
            columns_to_extract = ['DAY', 'MONTH', 'YEAR', 'HOUR', 'MINUTE', 'SECOND']
            values_of_first_valid_row = df.loc[0, columns_to_extract].astype(int).values
            datetime_format = '%d %m %Y %H %M %S'
            datetime_str = ' '.join(map(str, values_of_first_valid_row))
            datetime_obj = pd.to_datetime(datetime_str, format=datetime_format) + pd.Timedelta(hours=8) # Convert from GMT to GMT+8. (AWST)
            df = df.drop(index=0).reset_index(drop=True)

            df = df.drop(columns=['LAT', 'LON', 'DAY', 'MONTH', 'YEAR', 'HOUR', 'MINUTE', 'SECOND'])
            
            mask = np.logical_and([s.startswith('*') for s in df['ACCEL_X']], df.index % 1560 == 0)

            # # Calculates how many minutes since the initial date (based on the mask)
            seconds_to_add = np.zeros(len(df))
            seconds_to_add[mask] = np.arange(0, mask.sum()) * 60

            # Calculates a new date from the initial date for every minute
            df['DATE'] = None
            df.loc[mask, 'DATE'] = datetime_obj + pd.to_timedelta(seconds_to_add[mask], unit='s')
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

        except:
            print("Error: Cannot clean file")
            logger.error("Error: Cannot clean file __at class data_clean, clean_data function")

    @log_func_call()
    def start_clean_data(self, window, df):
        df_queue = queue.Queue()

        label = Label(window, text="Cleaning: ", font=("Helvetica", 16)) 
        label.place(relx=.5, rely=.5, x=100, y=-30, anchor=CENTER)   
        clean_pb = ttk.Progressbar(window, mode="indeterminate", style="TProgressbar")     
        clean_pb.place(relx=.5, rely=.5, x=100, anchor=CENTER, width=200)

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

    @log_func_call()
    def save_to_csv(self, df, file_name):
        df.to_csv(file_name, index=False)

    @log_func_call()
    def start_save_to_csv(self, cleaned_data, path, window):

        label = Label(window, text="Writing to CSV: ", font=("Helvetica", 16)) 
        label.place(relx=.5, rely=.5, x=100, y=-30, anchor=CENTER)     
        write_pb = ttk.Progressbar(window, mode="indeterminate", style="TProgressbar")   
        write_pb.place(relx=.5, rely=.5, x=100, anchor=CENTER, width=200)

        write_pb.start()

        thread = threading.Thread(target=ProcessData.save_to_csv, args=(self, cleaned_data, path))
        thread.start()

        while thread.is_alive():
            window.update()

        time.sleep(0.5)
        write_pb.destroy()
        label.destroy()