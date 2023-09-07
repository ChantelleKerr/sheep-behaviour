import os
import threading
import time

from data_cleaning.data_clean import SheepData


def process_flock(folder_path):
    sheep_folders = sorted(os.listdir(folder_path))
    threads = []
    for folder in sheep_folders:
        if folder.startswith("GPS"):
            sheep_data = SheepData()
            thread = threading.Thread(target=sheep_data.process, args=(folder,))
            thread.start()
            threads.append(thread)
    for thread in threads:
        thread.join()

## Application starting point
## Run python3 main.py or python main.py
if __name__ == "__main__":
    process_flock("test_data")
    