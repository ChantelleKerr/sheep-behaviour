import time
from tkinter import filedialog
from tkinter import ttk
from tkinter import *
import sys

from data_cleaning.data_clean import ProcessData

folder_path = None

#Get ("Load") folder with sheep files in it
def getFolder():
    global folder_path
    folder_path = filedialog.askdirectory()
    if not folder_path:
        return

    label = Label(second_frame, text="Successfully loaded: " + folder_path, font=("Helvetica", 18)) 
    label.grid(row=0, column=0, sticky="ew")
    clean_file_button["state"] = NORMAL

def cleanFiles(read_pb, clean_pb, write_pb, window):
    process_data = ProcessData()
    global combined_data
    global cleaned_data

    combined_data = process_data.read_data(folder_path, read_pb, window)

    print("Cleaning data in progress")
    cleaned_data = process_data.start_clean_data(clean_pb, window, combined_data)
    print("Completed data cleaning")

    print("Writing to CSV in progress")
    process_data.start_save_to_csv(cleaned_data, folder_path+"/cleaned.csv", write_pb, window)
    print("Completed writing")


## Application starting point
## Run python3 main.py or python main.py
if __name__ == "__main__":

    window = Tk()

    window.title("Sheep Behaviour Analysis")
    window.rowconfigure(0, minsize=800, weight=1)
    window.columnconfigure(1,minsize=800, weight=1)

    #Frames
    menu_frame = Frame(window, relief=RAISED, bd=2, bg="gray98")
    menu_frame.grid(row=0, column=0, sticky="ns")

    second_frame = Frame(window)
    second_frame.grid(row=0,column=1)

    #Progress Bars
    read_pb = ttk.Progressbar(window)
    clean_pb = ttk.Progressbar(window, mode="indeterminate")
    write_pb = ttk.Progressbar(window, mode="indeterminate")

    #Buttons
    load_file_button = Button(menu_frame, text='Load Files', command=getFolder) 
    load_file_button.grid(row=0, column=0, sticky="ew",padx=(5), pady=(5))

    clean_file_button = Button(menu_frame, text='Clean Files', state=DISABLED, command = lambda: cleanFiles(read_pb, clean_pb, write_pb, window))
    clean_file_button.grid(row=1, column=0, sticky="ew", padx=(10))

    window.mainloop()

