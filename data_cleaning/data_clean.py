import os

import numpy as np
import pandas as pd


class ProcessData():
    def read_data(self, folder_path):
        """
        We need to change this function it currently deletes any rows after it finds the header in the first 
        """
        dfs = []
        file_names = sorted(os.listdir(folder_path))
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

                if header_indices:
                    header_count += 1
            
                if header_count <= 2:
                    last_row_index = header_indices[0] if header_indices else None
                    if last_row_index is not None:
                        dfs.append(df.iloc[:last_row_index])
                    else:
                        dfs.append(df)
            
            
        combined_df = pd.concat(dfs, ignore_index=True)
        return combined_df
    
    # TODO : Handle different Hz, 
    #       convert time column to HH:MM:SS and add date column (or should this be combined?) - the acutal time and date needs to start from a given time and date.
    #       remove -2048, -2048,-2048 rows
    
    
    def clean_data(self, df):
        mask = df.iloc[:, 0].str.startswith('*')
        indices = df.loc[mask, df.columns[0]].str[1:].astype(int).ffill().fillna(0).astype(int)
        print(indices)
        df['seconds'] = indices
        df['seconds'] = df['seconds'].fillna(method='ffill').astype(int)


        df = df.loc[~mask].reset_index(drop=True)
        print(df)
        
        #zero_mask = (df.iloc[:, 0] == 0) & (df.iloc[:, 1] == 0) & (df.iloc[:, 2] == 0)
    
        #zero_indices = zero_mask.index[zero_mask]
   
        return df
        
    def save_to_csv(self, df, file_name):
        df.to_csv(file_name, index=False)





    
