import os
import time
import csv
from datetime import datetime, timedelta


def process_file(file):

    # Operation Structure (Modular)
    # READ 1: Read RAW Input file --> Calculate Avg HZ, Find Row of First Date Instance, Store Non-Zero Rows, Prepare Time Logic. 
    # WRITE 1:Initial Cleaning ->Write (NON-ZEROS, NON-DATE) filtered Rows, and Append Time. Add Header Row.

    clean_rows = []  # Store cleaned non-zero rows
    input_file = file  # Replace with the actual path to your text file
    first_date_instance = []
    date_row_number = 0
    final_row_count = 0

    # READ START TIME
    read_start_time = time.time()  

    # READ 1: READ RAW INPUT FILE AND START CALCULATIONS (Avg Hz is calculated from Number of Rows between each instance of "*")
    with open(input_file, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)

        found_11_column_row = False
        clean_rows = []  
        row_counts = []  # Store the number of rows between each "*".
        count = 0        # Count the rows between "*" occurrences.
        total_non_zero_rows = 0  # Total Count of non-zero rows.

        # Loop Through & Check: Count occurences of non-zero rows between each Astrisk Row "*" to get Avg Rows. (Avg Hz). Also check row of first date occurence.
        for row in reader:
            # HARD-CODED!: Check if the row contains exactly 11 columns (2023 Files)
            if len(row) == 11 and not found_11_column_row:
                last_six_elements = row[-6:]
                first_date_instance = [int(element) for element in last_six_elements]
                date_row_number = total_non_zero_rows
                print("")
                print("First row with 11 columns (row {}): {}".format(date_row_number, row))
                found_11_column_row = True

            if row and row[0].startswith('*'):
                try:
                    if count > 0:
                        row_counts.append(count)
                        count = 0
                except ValueError:
                    pass  # Ignore if conversion to integer fails
            else:
                if not all(value == '0' for value in row) and len(row) == 3:
                    clean_rows.append(row)
                    final_row_count += 1
                    total_non_zero_rows += 1
                    count += 1

        # Calculate the average row count between "*" and integer
        if row_counts:
            average_row_count = sum(row_counts) / len(row_counts)
            average_row_count = round(average_row_count,2)

            print("Average Hz: " + str(average_row_count))
        else:
            print("No '*' occurrences found.")

        # Print the total number of non-zero rows
        day, month, year, hour, minute, second = first_date_instance
        date_string = str(day) + '/' + str(month) + '/' + str(year)
        date_time = datetime(year, month, day, hour, minute, second)
        formatted_incremental_date_time = date_time.strftime("%H:%M:%S.%f")[:-2]

        print("Date Time: " +  formatted_incremental_date_time)
        print("Date String: " + date_string)
        print("")

    # TIME LOGIC.
    rewind_time = round((date_row_number / average_row_count))
    increment_time = round((1/average_row_count),4)
    formatted_incremental_date = date_time - timedelta(seconds=rewind_time)
    starting_date_time = formatted_incremental_date.strftime("%H:%M:%S.%f")[:-2]

    print("Final Row Count: " + str(final_row_count)) # Excluding Header Row That Will be Added in Wriote.
    print("Time to Rewind (seconds): " + str(rewind_time)) 
    print("Time Increment (seconds): " + str(increment_time))
    print("Starting Date Time: " +  starting_date_time)

    new_input_file = 'data/output.csv'
    
    # READ END TIME
    read_end_time = time.time()  # Record the start time
    read_execution_time = read_end_time - read_start_time  # Calculate the execution time

    # WRITE 2: WRITE (NON-ZEROS, NON-DATE) FILTERED ROWS + APPEND TIME FORMAT AND INCREMENT IN MICROSECONDS. (Consumes ~75% of Execution Time)
    # Precalculating String Formats: Memory Heavy?

    # WRITE START TIME
    write_start_time = time.time()

    formatted_datetime_strings = [dt.strftime("%H:%M:%S.%f")[:-2] for dt in ((formatted_incremental_date) + timedelta(seconds=i*increment_time) for i in range(len(clean_rows)))]
    # Batch Writing for optimisation?
    batch_size = 500000
    with open(new_input_file, 'w', newline='', buffering=8192) as csvfile:
        csv_writer = csv.writer(csvfile)
        rows_to_write = []

        for i, row in enumerate(clean_rows):
            # If First Row, create that Header Row. [ACCEL_X, ACCEL_Y, ACCEL_Z, D/M/Y]
            # if i == 0:
            #     # Add the header row above the original row at i == 0
            #     header_row = ["ACCEL_X", "ACCEL_Y", "ACCEL_Z", date_string]
            #     rows_to_write.append(header_row)
            #     rows_to_write.append(row)  # Push original values to i == 1
            #     row.append(formatted_datetime_strings[i]) 
            # # Check if the Row doesn't start with an asterisk.
            # else:
            row.append(date_string)
            row.append(formatted_datetime_strings[i]) 
            rows_to_write.append(row)
            if len(rows_to_write) >= batch_size:
                csv_writer.writerows(rows_to_write)
                rows_to_write = []

        if rows_to_write:
            csv_writer.writerows(rows_to_write)
    print("Datetime values appended and CSV file updated.")

    # WRITE END TIME
    write_end_time = time.time()
    write_execution_time = write_end_time - write_start_time  

    print("")
    print("Total Read Time: {:.2f} seconds".format(read_execution_time))
    print("Total Write Time: {:.2f} seconds".format(write_execution_time))


if __name__ == "__main__":

    # REPLACE INPUT_FILE PATH.
    input_file = 'data/file008.txt' 
    output_file = 'data/output.csv'

    start_time = time.time()  # Record the start time
    process_file(input_file)
    end_time = time.time()  # Record the end time
    execution_time = end_time - start_time  # Calculate the execution time
    estimated_time = (execution_time * 30)/60
    
    input_file_size = (os.path.getsize(input_file)) / (1024*1024)
    output_file_size = (os.path.getsize(output_file)) / (1024*1024)
    estimated_folder_size = output_file_size*30

    print("Total Execution Time: {:.2f} seconds".format(execution_time))
    print("Estimated Total Execution Time for Sheep Folder: {:.2f} mins".format(estimated_time))
    print("Total File Size: {:.2f}mb, (+{:.2f}mb, +{:.2f}%)".format(output_file_size, output_file_size-input_file_size, ((output_file_size-input_file_size)/input_file_size)*100))
    print("Estimated Total Folder Size: {:.2f}mb / {:.2f}gb".format(estimated_folder_size, (estimated_folder_size/1024)))
