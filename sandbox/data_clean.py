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
    def clean_data(self, df):
      mask = df.iloc[:, 0].str.startswith('*')
      indices = df.loc[mask, df.columns[0]].str[1:].astype(int).ffill().fillna(0).astype(int)
      df['seconds'] = indices

      # Forward fill the 4th column
      df['seconds'] = df['seconds'].fillna(method='ffill').astype(int)

      df = df.loc[~mask].reset_index(drop=True)
      return df
        
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


    
