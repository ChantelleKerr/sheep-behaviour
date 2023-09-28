import os
import sys
import time
import webbrowser
from tkinter import *
from tkinter import filedialog, messagebox, ttk

from data_cleaning.data_clean import ProcessData

folder_path = None
path_to_folder = None
sheep_name = None

#Get ("Load") folder with sheep files in it
def getFolder():
    global folder_path
    global path_to_folder
    global sheep_name
    
    folder_path = filedialog.askdirectory()
    if not folder_path:
        return

    #Get sheep name for clean file name
    folder_path_list = folder_path.rsplit("/", 1)
    path_to_folder = folder_path_list[0]
    sheep_name = folder_path_list[1]

    # Get a list of files in the selected folder
    files_in_folder = os.listdir(folder_path)

    # Check if there is only one file in the folder. Throw Error box if True.
    if len(files_in_folder) <= 1:
        messagebox.showerror("Error", "Please select a folder containing more than one data file.")
        return

    load_label = Label(second_frame, text="Successfully loaded: " + folder_path, font=("Helvetica", 18)) 
    load_label.grid(row=0, column=0, sticky="ew")
    clean_file_button["state"] = NORMAL

def cleanFiles(read_pb, clean_pb, write_pb, window):
    process_data = ProcessData()

    combined_data = process_data.read_data(folder_path, read_pb, window)

    # Only start cleaning process if we have data
    if len(combined_data) > 0:
        print("Cleaning data in progress")
        cleaned_data = process_data.start_clean_data(clean_pb, window, combined_data)
        combined_data = [] # free memory
        print("Completed data cleaning")

        clean_data_folder = path_to_folder+"/cleaned_data"

        if os.path.isdir(clean_data_folder) == False:
            os.mkdir(clean_data_folder)

        print("Writing to CSV in progress")
        process_data.start_save_to_csv(cleaned_data,clean_data_folder+"/"+sheep_name+".csv", write_pb, window)
        print("Completed writing")
        cleaned_data = [] # Free memory

        print(clean_data_folder)

        messagebox.showinfo("Success", "Successfully cleaned selected data files")
        webbrowser.open('file:///'+clean_data_folder)

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

    s = ttk.Style()
    s.theme_use("default")
    s.configure("TProgressbar", thickness=10)

    #Progress Bars
    read_pb = ttk.Progressbar(window, style="TProgressbar")
    clean_pb = ttk.Progressbar(window, mode="indeterminate", style="TProgressbar")
    write_pb = ttk.Progressbar(window, mode="indeterminate", style="TProgressbar")

    #Buttons
    load_file_button = Button(menu_frame, text='Load Files', command=getFolder) 
    load_file_button.grid(row=0, column=0, sticky="ew",padx=(10), pady=(5))

    clean_file_button = Button(menu_frame, text='Clean Files', state=DISABLED, command = lambda: cleanFiles(read_pb, clean_pb, write_pb, window))
    clean_file_button.grid(row=1, column=0, sticky="ew", padx=(10))

    window.mainloop()

