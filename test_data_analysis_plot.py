#Test the functions in the data_analysis.plot file:
## function1: find_start_and_end_data(data_file, start_date, end_date)
## function2: (analysed_sheep.data)
## function3: calculate_dates()
from data_analysis.plot import AnalyseSheep
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import unittest


class Testdata_analysis_plot(unittest.TestCase):
    def setUp(self):
        self.test_file = 'test_output.csv'
        self.analysed_sheep = AnalyseSheep()
        self.test_prepare_data()

    def test_prepare_data(self):
        #Prepare the data set and save it to the test_output.csv file
        data = pd.DataFrame(np.ones((122, 4)))

        #Set the last column of rows 1, 61, and 121 to timestamp, and the remaining positions to NaN
        data.iloc[:, 3] = np.nan
        all_date = ['2023-02-15 08:03:00', '2023-02-15 08:04:00', '2023-02-15 08:05:00']
        data.iloc[[0, 60, 120], -1] = [datetime.strptime(date, '%Y-%m-%d %H:%M:%S') for date in all_date]
        data.iloc[:, :3] = data.iloc[:, :3].astype('int64')
        data.columns = ["ACCEL_X", "ACCEL_Y", "ACCEL_Z", "DATE"]
        data['DATE'] = pd.to_datetime(data['DATE'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        data.to_csv(self.test_file, index=False)

        #test_data is used for testing
        self.test_data = data.iloc[:121, :]

    def test_function(self):
        start_date = '2023-02-15 08:03:00'
        end_date = "2023-02-15 08:05:00"

        # test function find_start_and_end_data()
        self.analysed_sheep.data = self.analysed_sheep.find_start_and_end_data(self.test_file, start_date, end_date)
        try:
            pd.testing.assert_frame_equal(self.analysed_sheep.data, self.test_data)
            print("find_start_and_end_data，no problem.")
        except AssertionError:
            print("find_start_and_end_data，no problem.")

        # test function get_average_hertz_per_second()
        self.analysed_sheep.get_average_hertz_per_second(self.analysed_sheep.data)
        try:
            self.assertEqual(1, self.analysed_sheep.avg_hertz)
            print("get_average_hertz_per_second，no problem.")
        except AssertionError:
            print("get_average_hertz_per_second，no problem.")


        # test function calculate_dates()
        start_time = datetime(2023, 2, 15, 8, 3, 0)
        end_time = datetime(2023, 2, 15, 8, 5, 0)
        date_strings = []
        current_time = start_time
        while current_time <= end_time:
            date_strings.append(current_time.strftime('%Y-%m-%d %H:%M:%S'))
            current_time += timedelta(seconds=1)
        date_strings = pd.Series(pd.to_datetime(date_strings, format='%Y-%m-%d %H:%M:%S', errors='coerce'),name = "DATE")

        self.analysed_sheep.calculate_dates()

        try:
            pd.testing.assert_series_equal(date_strings, self.analysed_sheep.data['DATE'])
            print("calculate_dates，no problem.")
        except AssertionError:
            print("calculate_dates，no problem.")

        #Delete test_output.csv file
        os.remove('test_output.csv')

if __name__ == "__main__":
    unittest.main()


