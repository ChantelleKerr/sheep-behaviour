from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.widgets import Slider


def find_start_and_end_data(data_file, start_date, end_date):
    df = pd.read_csv(data_file)

    
    start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    df['DATE'] = pd.to_datetime(df['DATE'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

    # Calculate the time difference for each given date and add them as new columns
    df['TimeDifference1'] = (df['DATE'] - start_date).abs().dt.total_seconds()
    df['TimeDifference2'] = (df['DATE'] - end_date).abs().dt.total_seconds()

    # Sort the DataFrame by the time differences for the first given date
    time_diff_df = df.sort_values(by='TimeDifference1')

    # Get the index of the row with the smallest time difference for the first given date
    closest_index1 = time_diff_df.index[0]

    # Sort the DataFrame by the time differences for the second given date
    time_diff_df = time_diff_df.sort_values(by='TimeDifference2')

    # Get the index of the row with the smallest time difference for the second given date
    closest_index2 = time_diff_df.index[0]
    df.drop(columns=['TimeDifference1', 'TimeDifference2'], inplace=True)

    # Get the data betwwen those two dates
    extracted_data = df.iloc[closest_index1:closest_index2 + 1]
    extracted_data.reset_index(drop=True, inplace=True)

    return extracted_data




def plot(df):
    x_accel = df.iloc[:, 0].tolist()
    y_accel = df.iloc[:, 1].tolist()
    z_accel = df.iloc[:, 2].tolist()
    time_values = df.iloc[:, 3].tolist() 

    fig, (ax_x, ax_y, ax_z) = plt.subplots(3, 1, sharex=True)

    
    line_x, = ax_x.plot(time_values, x_accel, linewidth=0.1)
    line_y, = ax_y.plot(time_values, y_accel, linewidth=0.1)
    line_z, = ax_z.plot(time_values, z_accel, linewidth=0.1)

    ax_x.set_ylabel('X acceleration')
    ax_y.set_ylabel('Y acceleration')
    ax_z.set_ylabel('Z acceleration')
    ax_z.set_xlabel('time (s)')

    ax_x.set_ylim(min(x_accel), max(x_accel))
    ax_y.set_ylim(min(y_accel), max(y_accel))
    ax_z.set_ylim(min(z_accel), max(z_accel))

    plt.tight_layout()
    plt.show()






# TODO: Get from user input
start_date = '2023-02-16 13:05:35'
end_date = '2023-02-16 13:10:00'
data_file = 'test_data/cleaned_data/GPS0028.csv'



# TODO Call this function when starting analysis button is clicked
data = find_start_and_end_data(data_file, start_date, end_date)


data['DATE'] = pd.to_datetime(data['DATE'], errors='coerce')

date_mask = data['DATE'].notna()
minute_indices = date_mask[date_mask].index

minute_counts = pd.Series(minute_indices).diff().fillna(minute_indices[0]).astype(int)
hertz_per_second = minute_counts[1:] / 60


print(hertz_per_second)
average_hertz_per_second = round(hertz_per_second.mean())
print(average_hertz_per_second)


current_date = data['DATE'].iloc[0]

updated_dates = []

mask = data.index % average_hertz_per_second == 0

indices_where_true = mask.nonzero()[0]

print(indices_where_true)

for index, row in data.iterrows():
    updated_dates.append(current_date)
    if mask[index] and index != 0:
        current_date += pd.DateOffset(seconds=1)

data['DATE'] = updated_dates

print(data)



plot(data)

