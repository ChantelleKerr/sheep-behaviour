from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.widgets import Slider


def find_start_and_end_data(data_file, start_date, end_date):
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
    pd.options.display.colheader_justify = 'center'

    time_diff_df = df.sort_values(by='TimeDifference1')
    closest_index1 = time_diff_df.index[0]
    time_diff_df = time_diff_df.sort_values(by='TimeDifference2')
    closest_index2 = time_diff_df.index[0]

    df.drop(columns=['TimeDifference1', 'TimeDifference2'], inplace=True)


    # Get the data betwwen those two dates
    extracted_data = df.iloc[closest_index1:closest_index2 + 1]
    extracted_data.reset_index(drop=True, inplace=True)

    return extracted_data


def get_average_hertz_per_second(data):
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


def calculate_dates(data, avg_hertz):
    '''
    Since we only have dates for every minute we need to calculate the dates inbetween based on the average hertz
    '''
    initial_date = data['DATE'].iloc[0]
    print(initial_date)
    num_rows = len(data)
    print(num_rows)
    
    time_diff_seconds = 1 / avg_hertz
    print(time_diff_seconds)
    
    timedelta_array = np.arange(num_rows) * pd.Timedelta(seconds=time_diff_seconds)
    print(timedelta_array)
    data['DATE'] = initial_date + timedelta_array
    print(data)


    return data



def plot(df):
    x_accel = df.iloc[:, 0].tolist()
    y_accel = df.iloc[:, 1].tolist()
    z_accel = df.iloc[:, 2].tolist()
    time_values = df.iloc[:, 3].tolist() 

    # Calcuate the mean for every minute (not sure if needed so commenting out for now)
    # df.set_index('DATE', inplace=True)
    # resampled_df = df.resample('1T').mean()
    # print(resampled_df)

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




def start_analysis(data_file, start_date, end_date):
    '''
    Function that is run when the "Start Analysis" button is pressed
    data_file, start_date, end_date should be passed as valid inputs
    '''
    
    data = find_start_and_end_data(data_file, start_date, end_date)
    avg_hertz = get_average_hertz_per_second(data)
    data = calculate_dates(data, avg_hertz)
    plot(data)
