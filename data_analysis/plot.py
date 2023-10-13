import copy
import csv
import os
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class AnalyseSheep():
    def __init__(self):
        self.data = []
        self.start_date = None
        self.end_date = None
        self.folder_path = None
        self.current_plot = None
        self.sheep = None
        self.plot_mode = None
        self.avg_hertz = None

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


        # Get the data between those two dates
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

        self.avg_hertz = round(hertz_per_second.mean())
        


    def calculate_dates(self):
        '''
        Since we only have dates for every minute we need to calculate the dates inbetween based on the average hertz
        '''
        initial_date = self.data['DATE'].iloc[0]
        num_rows = len(self.data)
        
        time_diff_seconds = 1 / self.avg_hertz
        
        timedelta_array = np.arange(num_rows) * pd.Timedelta(seconds=time_diff_seconds)
        
        self.data['DATE'] = initial_date + timedelta_array


    def plot(self):
        x_accel = self.data.iloc[:, 0].tolist()
        y_accel = self.data.iloc[:, 1].tolist()
        z_accel = self.data.iloc[:, 2].tolist()
        time_values = self.data.iloc[:, 3].tolist() 

        fig, (ax_x, ax_y, ax_z) = plt.subplots(3, 1, sharex=True)
        ax_x.set_title(self.sheep)

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
        self.current_plot = plt
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
        plt.title(f'Total Amplitude Sum {self.sheep}')
        plt.plot(time_values, self.data['total_sum'], label='Total Amplitude Sum', marker='o', markersize=0.5, linestyle='-', linewidth=0.5)
        plt.xlabel('Time Values')
        plt.ylabel('Total Amplitude Sum (Normalised)')
        
        plt.legend()
        plt.grid(True)
        self.current_plot = plt
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
        self.get_average_hertz_per_second(self.data)
        self.calculate_dates()
        self.sheep = os.path.basename(self.folder_path).split(".")[0]
        self.plot()


    def generate_report(self):
        accel_data = self.data.iloc[:, :3]

        mean_values = accel_data.mean().round(2)
        mode_values = accel_data.mode().iloc[0].round(2)  # Use .iloc[0] (might have multiple modes)
        median_values = accel_data.median().round(2)
        std_values = accel_data.std().round(2)

        stat_folder = os.path.dirname(self.folder_path)
        report_dir = os.path.join(stat_folder, "reports", self.plot_mode)
        os.makedirs(report_dir, exist_ok=True) 

        output_file = os.path.join(report_dir, "stats.csv")
        file_exists = os.path.exists(output_file)

        with open(output_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            
            if not file_exists:
                writer.writerow(['SHEEP', 'START DATE', 'END DATE', 'ACCEL_X_MEAN', 'ACCEL_X_MODE', 'ACCEL_X_MEDIAN', 'ACCEL_X_STD',
                                 'ACCEL_Y_MEAN', 'ACCEL_Y_MODE', 'ACCEL_Y_MEDIAN', 'ACCEL_Y_STD',
                                 'ACCEL_Z_MEAN', 'ACCEL_Z_MODE', 'ACCEL_Z_MEDIAN', 'ACCEL_Z_STD'])
            
            writer.writerow([self.sheep, self.start_date, self.end_date,
                             mean_values['ACCEL_X'], mode_values['ACCEL_X'], median_values['ACCEL_X'], std_values['ACCEL_X'],
                             mean_values['ACCEL_Y'], mode_values['ACCEL_Y'], median_values['ACCEL_Y'], std_values['ACCEL_Y'],
                             mean_values['ACCEL_Z'], mode_values['ACCEL_Z'], median_values['ACCEL_Z'], std_values['ACCEL_Z']])

    # Used to write analysed data to a file
    # Has dates in all rows 
    def write_to_file(self):
        path = os.path.dirname(self.folder_path)
        plot_dir = os.path.join(path, "plots", self.plot_mode)
        os.makedirs(plot_dir, exist_ok=True) 
        filename = f"{self.sheep}_plot_data.csv"
        file_path = os.path.join(plot_dir, filename)
        self.data.to_csv(file_path, index=False)

    # The plot must be open!
    def export_plot(self):
        path = os.path.dirname(self.folder_path)
        plot_dir = os.path.join(path, "plots", self.plot_mode)
        os.makedirs(plot_dir, exist_ok=True) 
        filename = f"{self.sheep}.png"
        file_path = os.path.join(plot_dir, filename)
        if self.current_plot:
            self.current_plot.savefig(file_path, format='png')




# start_date = '2023-02-16 13:05:35'
# end_date = '2023-02-16 13:10:00'
# data_file = 'test_data/GPS0028.csv'
# p = AnalyseSheep()
# p.start_analysis(data_file, start_date, end_date)
# p.export_to_pdf()
# p.write_to_file()
