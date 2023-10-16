from data_cleaning.data_clean import ProcessData
import queue
from tkinter import *
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import unittest
import shutil

# Prepare test data set
lines1 = ['ACCEL_X,ACCEL_Y,ACCEL_Z,LAT,LON,DAY,MONTH,YEAR,HOUR,MINUTE,SECOND',
            '1,1,1',
            '1,1,1']
lines2 = ['*0,0,0,0,0,15,2,2023,0,3,11',
            '1,1,1',
            '1,1,1',
            '1,1,1',
            '0,0,0',
            '0,0,0,0,0,15,2,2023,0,3,12']
test_folder = "./test_data"
data = [
    [0, 0, 0, 0, 0, 15, 2, 2023, 0, 3, 11],
    [1, 1, 1] + [np.nan] * 8,
    [1, 1, 1] + [np.nan] * 8,
    [1, 1, 1] + [np.nan] * 8,
    [0, 0, 0] + [np.nan] * 8,
    [0, 0, 0, 0, 0, 15, 2, 2023, 0, 3, 12]
]
data_array = np.array([np.array(row) for row in data])
df = pd.DataFrame(data_array)
df.columns = ['ACCEL_X', 'ACCEL_Y', 'ACCEL_Z', 'LAT', 'LON', 'DAY', 'MONTH', 'YEAR', 'HOUR', 'MINUTE', 'SECOND']
df[['ACCEL_X', 'ACCEL_Y', 'ACCEL_Z']] = df[['ACCEL_X', 'ACCEL_Y', 'ACCEL_Z']].astype('int64')
df[['ACCEL_X']] = df[['ACCEL_X']].astype('str')
df.iloc[0, 0] = '*0'

class TestProcessData(unittest.TestCase):
    
    def test_process_data(self):
        # Set storage path
        if not os.path.exists(test_folder):
            os.makedirs(test_folder)

        # Write the data set to the path and save it as a txt file
        for i in range(2):
            output_file = test_folder + '/file' + '{:03d}'.format(i) + '.txt'
            if i == 0:
                lines = lines1
            else:
                lines = lines2
            content = '\n'.join(lines)
            with open(output_file, 'w') as file:
                file.write(content)

        # Testing officially begins

        ## 1.Test start_read_data()

        ### Use the function under test
        process_data = ProcessData()
        root = Tk()
        test_df = process_data.start_read_data(test_folder, root)
        #root.destroy()
        ### Prediction data set
        
        ### Test if they are the same
        pd.testing.assert_frame_equal(df, test_df, "Raw data frames are not equal")


        ## 2.Test the start_clean_data() function
        ### Use the function under test
        #root = Tk()
        cleaned_test_df = process_data.start_clean_data(root, test_df)
        #root.destroy()
        ### Prejudgment data collection
        cleaned_df = df.iloc[1:4, 0:4].copy()
        cleaned_df.columns = ['ACCEL_X', 'ACCEL_Y', 'ACCEL_Z', 'DATE']
        cleaned_df.iloc[0:3, 3] = None
        cleaned_df.iloc[:, 0] = cleaned_df.iloc[:, 0].astype("str")
        cleaned_df = cleaned_df.reset_index(drop=True)
        
        ### Test if they are the same
        pd.testing.assert_frame_equal(cleaned_df, cleaned_test_df, "Cleaned data frames are not equal")

        ## 3.Test the start_save_to_csv() function
        ### Use the function under test
        #root = Tk()
        process_data.start_save_to_csv(cleaned_df, "test.csv", root)
        root.destroy()

        ### Check if a dataset file exists
        if os.path.exists("test.csv"):
            saved_test_df = pd.read_csv('test.csv')
            saved_test_df.iloc[:, 0] = saved_test_df.iloc[:, 0].astype("str")
            saved_test_df.iloc[:, 3] = None
            
        pd.testing.assert_frame_equal(cleaned_df, saved_test_df, "Saved csv error")

        # Delete created files and folders
        shutil.rmtree(test_folder)
        os.remove("test.csv")

if __name__ == "__main__":
    unittest.main()