import os

import numpy as np
import pandas as pd


class ProcessData():
    def read_data(self, folder_path):
        dfs = []
        file_names = sorted(os.listdir(folder_path))
        print(file_names)
        is_first = True  # Start by assuming the first file has a header
        header_count = 0


        for file in file_names:
            print(file)
            if file.endswith('.txt'):
                file_path = os.path.join(folder_path, file)
                skiprows = 1 if is_first else None
                df = pd.read_csv(file_path, usecols=range(3), header=None, skiprows=skiprows)
                # dfs.append(df)
                df_array = df.to_numpy()
                print(df)
                is_first = False

                header_indices = np.where(np.all(df_array[:, :1] == "ACCEL_X", axis=1))[0].tolist()           
                print("******", header_indices)

                if header_indices:
                    header_count += 1
            
                if header_count <= 2:
                    last_row_index = header_indices[0] if header_indices else None
                    if last_row_index is not None:
                        dfs.append(df.iloc[:last_row_index])
                    else:
                        dfs.append(df)
            
            
        combined_df = pd.concat(dfs, ignore_index=True)
        #combined_df = combined_df[['ACCEL_X', 'ACCEL_Y', 'ACCEL_Z']]
        return combined_df
    
    # TODO : Handle different Hz, 
    #       convert time column to HH:MM:SS and add date column (or should this be combined?) - the acutal time and date needs to start from a given time and date.
    #       note: havent handled headers because the data files i was processing didnt have it
    
    
    def clean_data(self, df):
        mask = df.iloc[:, 0].str.startswith('*')
        indices = df.loc[mask, df.columns[0]].str[1:].astype(int).ffill().fillna(0).astype(int)
        print(indices)
        df['seconds'] = indices
        df['seconds'] = df['seconds'].fillna(method='ffill').astype(int)


        df = df.loc[~mask].reset_index(drop=True)
        print(df)
        
        zero_mask = (df.iloc[:, 0] == 0) & (df.iloc[:, 1] == 0) & (df.iloc[:, 2] == 0)
    
        zero_indices = zero_mask.index[zero_mask]
    
        non_zero_indices = zero_mask.index[~zero_mask]
        
        nearest_non_zero = np.searchsorted(non_zero_indices, zero_indices, side='right') - 1
        
        df.iloc[zero_indices, :3] = df.iloc[non_zero_indices[nearest_non_zero], :3].values
    
        
                
        return df
        
    def save_to_csv(self, df, file_name):
        df.to_csv(file_name, index=False)


if __name__ == "__main__":
    process_data = ProcessData()
    folder_path = "data"  # didnt save data files in repo its too large (youll need to add your own datafile)
    combined_data = process_data.read_data(folder_path)
    cleaned_data = process_data.clean_data(combined_data)
    #print(cleaned_data)
    process_data.save_to_csv(cleaned_data, "data/cleaned.csv") 


    
