from data_cleaning.data_clean import ProcessData

## Application starting point
## Run python3 main.py or python main.py
if __name__ == "__main__":
    process_data = ProcessData()
    folder_path = "test_data/sheep1"  # didnt save data files in repo its too large (youll need to add your own datafile)
    combined_data = process_data.read_data(folder_path)
    cleaned_data = process_data.clean_data(combined_data)
    #print(cleaned_data)
    process_data.save_to_csv(cleaned_data, "test_data/sheep1/cleaned.csv") 