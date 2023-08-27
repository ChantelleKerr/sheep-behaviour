import time

from data_cleaning.data_clean import ProcessData

#from data_cleaning.multiprocess import ProcessData



## Application starting point
## Run python3 main.py or python main.py
if __name__ == "__main__":
    start_time = time.time()
    process_data = ProcessData()
    folder_path = "test_data/sheep1"  # hardcoded data path
    combined_data = process_data.read_data(folder_path)
   
    cleaned_data = process_data.clean_data(combined_data)
    
    print(cleaned_data)
    process_data.save_to_csv(cleaned_data, "test_data/sheep1/cleaned.csv") 
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")