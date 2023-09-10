import time
from tkinter import filedialog
from tkinter import ttk
from tkinter import *
import sys

from data_cleaning.data_clean import ProcessData

folder_path = None
combined_data = None
cleaned_data = None

def getFolder():
    global folder_path
    folder_path = filedialog.askdirectory()
    if not folder_path:
        return

    label = Label(second_frame, text="Successfully loaded: " + folder_path, font=("Helvetica", 18)) 
    label.grid(row=0, column=0, sticky="ew")
    clean_file_button["state"] = NORMAL

def cleanFiles(progressbar, progressbar2, progressbar3, window):
    process_data = ProcessData()
    global combined_data
    global cleaned_data


    combined_data = process_data.read_data(folder_path, progressbar, window)
    print("Cleaning data in progress")
    cleaned_data = process_data.start_clean_data(process_data.clean_data, progressbar2, window, combined_data)
    print("Completed data cleaning")

    print("Writing to CSV in progress")
    process_data.start_save_to_csv(process_data.save_to_csv, cleaned_data, folder_path+"/cleaned.csv", progressbar3, window)
    print("Completed writing")


## Application starting point
## Run python3 main.py or python main.py
if __name__ == "__main__":

    window = Tk()

    window.title("Sheep Behaviour Analysis")
    window.rowconfigure(0, minsize=800, weight=1)
    window.columnconfigure(1,minsize=800, weight=1)

    menu_frame = Frame(window, relief=RAISED, bd=2, bg="gray98")
    menu_frame.grid(row=0, column=0, sticky="ns")

    second_frame = Frame(window)
    second_frame.grid(row=0,column=1)

    progressbar = ttk.Progressbar(window)
    progressbar2 = ttk.Progressbar(window, mode="indeterminate")
    progressbar3 = ttk.Progressbar(window, mode="indeterminate")

    load_file_button = Button(menu_frame, text='Load Files', command=getFolder) 
    load_file_button.grid(row=0, column=0, sticky="ew",padx=(5), pady=(5))

    clean_file_button = Button(menu_frame, text='Clean Files', state=DISABLED, command = lambda: cleanFiles(progressbar, progressbar2, progressbar3, window))

    clean_file_button.grid(row=1, column=0, sticky="ew", padx=(10))

    window.mainloop()

