


import os
import pandas as pd

class ProcessData():
    def read_data(self, folder_path):
        dfs = []
        file_names = sorted(os.listdir(folder_path))
        print(file_names)

        for file in file_names:
            print(file)
            if file.endswith('.txt'):
                file_path = os.path.join(folder_path, file)
                df = pd.read_csv(file_path, usecols=range(3), header=None)
                dfs.append(df)
        combined_df = pd.concat(dfs, ignore_index=True)
        return combined_df
    
    # TODO : Handle different Hz, 
    #       convert time column to HH:MM:SS and add date column (or should this be combined?) - the acutal time and date needs to start from a given time and date.
    #       note: havent handled headers because the data files i was processing didnt have it
    #       It takes time to process the data of only 4 files so we will need to optimise it if possible
    def clean_data(self, df):
        cleaned_rows = []

        current_index = None
        combined_rows = []

        for index, row in df.iterrows():
            print(index, len(df))
            if row.iloc[0].startswith('*'):
                current_index = row.iloc[0][1:]

                if combined_rows:
                    combined_rows = [r + [current_index] for r in combined_rows]
                    cleaned_rows.extend(combined_rows)

                combined_rows = []
            else:
                combined_rows.append(list(row))

        if combined_rows and current_index:
            combined_rows = [r + [current_index] for r in combined_rows]
            cleaned_rows.extend(combined_rows)
        return pd.DataFrame(cleaned_rows)
        
    def save_to_csv(self, df, file_name):
        df.to_csv(file_name, index=False)
        

if __name__ == "__main__":
    process_data = ProcessData()
    folder_path = "data"  # didnt save data files in repo its too large (youll need to add your own datafile)
    combined_data = process_data.read_data(folder_path)
    print(combined_data)
    cleaned_data = process_data.clean_data(combined_data)
    print(cleaned_data)
    process_data.save_to_csv(cleaned_data, "data/cleaned.csv") 


    
