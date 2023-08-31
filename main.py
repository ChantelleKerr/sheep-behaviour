import time

from data_cleaning.data_clean import ProcessData

## Application starting point
## Run python3 main.py or python main.py
if __name__ == "__main__":
    start_time = time.time()
    
    process_data = ProcessData()
    folder_path = "test_data/sheep1"  # hardcoded data path
    
    read_time = time.time()
    print("Reading file in progress")
    combined_data = process_data.read_data(folder_path)
    read_end_time = time.time()
    print("Completed file read")
   
    print("Cleaning data in progress")
    start_clean_time = time.time()
    cleaned_data = process_data.clean_data(combined_data)
    end_clean_time = time.time()
    print("Completed data cleaning")
    
    print("Writing to CSV in progress")
    start_write_time = time.time()
    process_data.save_to_csv(cleaned_data, "test_data/sheep1/cleaned.csv")
    end_write_time = time.time()
    print("Completed writing")


    end_time = time.time()
    
    total_read_time = read_end_time - read_time
    total_clean_time = end_clean_time - start_clean_time 
    total_write_time = end_write_time - start_write_time
    elapsed_time = end_time - start_time

    print(f"Read time: {total_read_time} seconds")
    print(f"Clean time: {total_clean_time} seconds")
    print(f"Write time: {total_write_time} seconds")
    print(f"Total Elapsed time: {elapsed_time} seconds")