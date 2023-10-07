from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import csv


class AnalyseSheep():
    def __init__(self):
        self.data = []
        self.start_date = None
        self.end_date = None
        self.folder_path = None

    def find_start_and_end_data(self, data_file, start_date, end_date):
        """
        Finds the rows nearest to start and end dates and return the data inbetween those dates.
        """
        df = pd.read_csv(data_file)

        
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        df['DATE'] = pd.to_datetime(df['DATE'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

        # Calculate the time difference for each given date and add them as new columns
        df['TimeDifference1'] = (df['DATE'] - start_date).abs().dt.total_seconds()
        df['TimeDifference2'] = (df['DATE'] - end_date).abs().dt.total_seconds()

        # Sort the DataFrame by the time differences for the given dates and get the closest date
        # TODO: What happens when it cant find a date?

        time_diff_df = df.sort_values(by='TimeDifference1')
        closest_index1 = time_diff_df.index[0]
        time_diff_df = time_diff_df.sort_values(by='TimeDifference2')
        closest_index2 = time_diff_df.index[0]

        df.drop(columns=['TimeDifference1', 'TimeDifference2'], inplace=True)


        # Get the data betwwen those two dates
        extracted_data = df.iloc[closest_index1:closest_index2 + 1]
        extracted_data.reset_index(drop=True, inplace=True)

        return extracted_data


    def get_average_hertz_per_second(self, data):
        """
        Calculate the average hertz across every minute to find the average hertz across every second
        """
        data['DATE'] = pd.to_datetime(data['DATE'], errors='coerce')

        date_mask = data['DATE'].notna()
        minute_indices = date_mask[date_mask].index

        minute_counts = pd.Series(minute_indices).diff().fillna(minute_indices[0]).astype(int)
        hertz_per_second = minute_counts[1:] / 60

        average_hertz_per_second = round(hertz_per_second.mean())
        return average_hertz_per_second


    def calculate_dates(self, data, avg_hertz):
        '''
        Since we only have dates for every minute we need to calculate the dates inbetween based on the average hertz
        '''
        initial_date = data['DATE'].iloc[0]
        num_rows = len(data)
        
        time_diff_seconds = 1 / avg_hertz
        
        timedelta_array = np.arange(num_rows) * pd.Timedelta(seconds=time_diff_seconds)
        
        data['DATE'] = initial_date + timedelta_array

        return data


    def plot(self, df):
        x_accel = df.iloc[:, 0].tolist()
        y_accel = df.iloc[:, 1].tolist()
        z_accel = df.iloc[:, 2].tolist()
        time_values = df.iloc[:, 3].tolist() 

        fig, (ax_x, ax_y, ax_z) = plt.subplots(3, 1, sharex=True)

        ax_x.plot(time_values, x_accel, marker='o', markersize=0.5, linestyle='-', linewidth=0.5, label='X acceleration')
        ax_y.plot(time_values, y_accel, marker='o', markersize=0.5, linestyle='-', linewidth=0.5, label='Y acceleration')
        ax_z.plot(time_values, z_accel, marker='o', markersize=0.5, linestyle='-', linewidth=0.5, label='Z acceleration')

        ax_x.set_ylabel('X acceleration')
        ax_y.set_ylabel('Y acceleration')
        ax_z.set_ylabel('Z acceleration')
        ax_z.set_xlabel('time (HH:MM:SS)')

        ax_x.set_ylim(min(x_accel), max(x_accel))
        ax_y.set_ylim(min(y_accel), max(y_accel))
        ax_z.set_ylim(min(z_accel), max(z_accel))

        plt.xticks(rotation=45)

        ax_x.yaxis.grid(True)
        ax_y.yaxis.grid(True)
        ax_z.yaxis.grid(True)

        plt.tight_layout()
        plt.show()


    def plot_amplitude(self):
        # Normalise the data (shift mean to zero)
        self.data[['ACCEL_X', 'ACCEL_Y', 'ACCEL_Z']] = (self.data[['ACCEL_X', 'ACCEL_Y', 'ACCEL_Z']] - self.data[['ACCEL_X', 'ACCEL_Y', 'ACCEL_Z']].mean()) / self.data[['ACCEL_X', 'ACCEL_Y', 'ACCEL_Z']].std()

        # Take the absolute values of the normalised dara
        self.data[['ACCEL_X', 'ACCEL_Y', 'ACCEL_Z']] = self.data[['ACCEL_X', 'ACCEL_Y', 'ACCEL_Z']].abs()

        # Calculate the sum of the absolute values for each row
        self.data['total_sum'] = self.data[['ACCEL_X', 'ACCEL_Y', 'ACCEL_Z']].sum(axis=1)
        time_values = self.data.iloc[:, 3].tolist()

        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.plot(time_values, self.data['total_sum'], label='Total Amplitude Sum', marker='o', markersize=0.5, linestyle='-', linewidth=0.5)
        plt.xlabel('Time Values')
        plt.ylabel('Total Amplitude Sum (Normalised)')
        plt.title('Time Values vs. Total Amplitude Sum')
        plt.legend()
        plt.grid(True)
        plt.show()


    def start_analysis(self, data_file, start_date, end_date):
        '''
        Function that is run when the "Start Analysis" button is pressed
        data_file, start_date, end_date should be passed as valid inputs
        '''
        self.start_date = start_date
        self.end_date = end_date
        self.folder_path = data_file
        self.data = self.find_start_and_end_data(data_file, start_date, end_date)
        avg_hertz = self.get_average_hertz_per_second(self.data)
        data = self.calculate_dates(self.data, avg_hertz)
        self.plot(data)


    def generate_report(self):
        self.data = self.data.drop(columns=['DATE'])

        mean_values = self.data.mean().round(2)
        mode_values = self.data.mode().iloc[0].round(2)  # Use .iloc[0] (might have multiple modes)
        median_values = self.data.median().round(2)
        std_values = self.data.std().round(2)

        stat_folder = os.path.dirname(self.folder_path)
        file = os.path.basename(self.folder_path)

        output_file = stat_folder + "/stats.csv"
        file_exists = os.path.exists(output_file)

        with open(output_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            
            if not file_exists:
                writer.writerow(['SHEEP', 'START DATE', 'END DATE', 'ACCEL_X_MEAN', 'ACCEL_X_MODE', 'ACCEL_X_MEDIAN', 'ACCEL_X_STD',
                                 'ACCEL_Y_MEAN', 'ACCEL_Y_MODE', 'ACCEL_Y_MEDIAN', 'ACCEL_Y_STD',
                                 'ACCEL_Z_MEAN', 'ACCEL_Z_MODE', 'ACCEL_Z_MEDIAN', 'ACCEL_Z_STD'])
            
            writer.writerow([file, self.start_date, self.end_date,
                             mean_values['ACCEL_X'], mode_values['ACCEL_X'], median_values['ACCEL_X'], std_values['ACCEL_X'],
                             mean_values['ACCEL_Y'], mode_values['ACCEL_Y'], median_values['ACCEL_Y'], std_values['ACCEL_Y'],
                             mean_values['ACCEL_Z'], mode_values['ACCEL_Z'], median_values['ACCEL_Z'], std_values['ACCEL_Z']])

    # Used to write analysed data to a file
    # Has dates in all rows 
    def write_to_file(self):
        path = os.path.dirname(self.folder_path)
        sheep = os.path.basename(self.folder_path).split(".")[0]
        self.data.to_csv(path + f"/{sheep}_all_times", index=False)




# start_date = '2023-02-16 13:05:35'
# end_date = '2023-02-16 13:10:00'
# data_file = 'test_data/GPS0028.csv'
# p = AnalyseSheep()
# p.start_analysis(data_file, start_date, end_date)
# p.write_to_file()