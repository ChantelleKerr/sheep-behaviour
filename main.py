import os
import sys
import time
import webbrowser
import threading
from queue import Queue
from tkinter import *
from tkinter import filedialog, messagebox, ttk

from data_cleaning.data_clean import ProcessData
from data_cleaning.data_clean_threaded import ProcessData_Threaded

folder_path = None
path_to_folder = None
sheep_name = None
active_labels = []

path_to_cleaned_data_batch = None
folder_paths = []            

global_var_lock = threading.Lock()


#Get ("Load") folder with sheep files in it
def getFolder():
    global folder_path
    global path_to_folder
    global sheep_name

    for label in active_labels:
        label.grid_remove()
    active_labels.clear()
    
    folder_path = filedialog.askdirectory()
    if not folder_path:
        return

    #Get sheep name for clean file name
    folder_path_list = folder_path.rsplit("/", 1)
    path_to_folder = folder_path_list[0]
    sheep_name = folder_path_list[1]
    clean_file_button["state"] = NORMAL

    # Get a list of files in the selected folder
    files_in_folder = os.listdir(folder_path)

    # Check if there is only one file in the folder. Throw Error box if True.
    if len(files_in_folder) <= 1:
        messagebox.showerror("Error", "Please select a folder containing more than one data file.")
        return

    load_label = Label(second_frame, text="Successfully loaded: " + folder_path, font=("Helvetica", 18)) 
    load_label.grid(row=0, column=0, sticky="ew")
    active_labels.append(load_label)

# MULTITHREADED: Batch Selection
def getFolders():
    global folder_paths
    global active_labels 

    for label in active_labels:
        label.grid_remove()
    active_labels.clear()

    label_count = 0
    while True:
        folder_path = filedialog.askdirectory()

        if not folder_path:
            print(folder_paths)
            break  # User clicked Cancel or closed the dialog
        else: 
            
            # ERROR-HANDLING: Check if only <= 1 file in the folder. Break Selection if True.
            files_in_folder = os.listdir(folder_path)
            print(files_in_folder)
            if len(files_in_folder) <= 1:
                messagebox.showerror("Error", "Please select a folder containing more than one data file.")
                print("ERROR")
                load_batch_button["state"] = NORMAL
                clean_batch_button["state"] = DISABLED
                folder_paths.pop()
                break

            # Otherwise: Update GUI and add Path to Array.
            folder_paths.append(folder_path)
            load_label_batch = Label(second_frame, text="Successfully loaded: " + folder_path, font=("Helvetica", 18)) 
            load_label_batch.grid(row=label_count, column=0, sticky="ew")
            active_labels.append(load_label_batch)

            if len(folder_paths) == 3:
                load_batch_button["state"] = DISABLED
                break


            print(folder_path)
         # Update the label with the selected folder paths
        label_count += 1
    print(folder_paths)

    if len(folder_paths) == 0:
        load_batch_button["state"] = NORMAL
        clean_batch_button["state"] = DISABLED
    else: 
        load_batch_button["state"] = DISABLED
        clean_batch_button["state"] = NORMAL

def cleanFiles(read_pb, clean_pb, write_pb, window):
    process_data = ProcessData()
    combined_data = process_data.read_data(folder_path, read_pb, window)

    print("Cleaning data in progress")
    cleaned_data = process_data.start_clean_data(clean_pb, window, combined_data)
    combined_data = [] # free memory
    print("Completed data cleaning")

    clean_data_folder = path_to_folder+"/cleaned_data_"
    if os.path.isdir(clean_data_folder) == False:
        os.mkdir(clean_data_folder)

    print("Writing to CSV in progress")
    process_data.start_save_to_csv(cleaned_data,clean_data_folder+"/"+sheep_name+".csv", write_pb, window)
    print("Completed writing")
    cleaned_data = [] # Free memory

    print(clean_data_folder)
    messagebox.showinfo("Success", "Successfully cleaned selected data files.")
    webbrowser.open('file:///'+clean_data_folder)

# MULTITHREADED: Batch Cleaning
def clean_files_thread(folder_path):
    global_var_lock.acquire()
    try:
        process_data = ProcessData_Threaded()
        combined_data = process_data.read_data(folder_path)

        #Get sheep name for clean file name
        folder_path_list = folder_path.rsplit("/", 1)
        path_to_folder = folder_path_list[0]
        sheep_name = folder_path_list[1]

        print("Cleaning data in progress")
        cleaned_data = process_data.start_clean_data(combined_data)
        combined_data = []  # Free memory
        print("Completed data cleaning")

        clean_data_folder = path_to_folder + "/cleaned_data_batch"
        
        global path_to_cleaned_data_batch
        path_to_cleaned_data_batch = clean_data_folder

        if not os.path.isdir(clean_data_folder):
            os.mkdir(clean_data_folder)

        print("Writing to CSV in progress")
        process_data.start_save_to_csv(cleaned_data, clean_data_folder + "/" + sheep_name + ".csv")
        print("Completed writing")
        cleaned_data = []  # Free memory
        print(clean_data_folder)
        
    finally:
    # Release the lock after modifying the array
        global_var_lock.release()

# Handle Multithreading for Folders
def multithread_clean_folders(folder_paths):

    threading_pb = ttk.Progressbar(window, mode="indeterminate", style="TProgressbar")
    threading_pb.start()  # Start the progress bar

    def gui_wrapper():

        # Fixes Bug by Creating new GUI.
        label = Label(window, text="Batch Cleaning... " + str(len(folder_paths)) + " Folder(s).", font=("Helvetica", 12)) 
        label.place(x=120, y=10)        
        threading_pb.place(x=120, y=40, width=200)

        global path_to_cleaned_data_batch
        start_time = time.time()
        print()
        threads = []
        for folder_path in folder_paths:
            thread = threading.Thread(target=clean_files_thread, args=(folder_path,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed Thrading Time: {elapsed_time} seconds")
        
        while any(thread.is_alive() for thread in threads):
            window.update()
 
        threading_pb.stop()
        messagebox.showinfo("Success", "Successfully cleaned selected data folders.")
        webbrowser.open('file:///'+ path_to_cleaned_data_batch)
        path_to_cleaned_data_batch = None # Free Up Path
        multithread_reset()
        threading_pb.destroy()
        label.destroy()

    thread = threading.Thread(target=gui_wrapper)
    thread.start()

def multithread_reset():
    global folder_paths
    folder_paths = [] # FREE THREADING FILE PATHS.
    load_batch_button["state"] = NORMAL
    clean_batch_button["state"] = DISABLED


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

    load_batch_button = Button(menu_frame, text='Load Batch', command=getFolders, state=NORMAL) 
    load_batch_button.grid(row=2, column=0, sticky="ew",padx=(10), pady=(5))

    clean_batch_button = Button(menu_frame, text='Clean Batch', state=DISABLED, command = lambda: multithread_clean_folders(folder_paths)) 
    clean_batch_button.grid(row=3, column=0, sticky="ew",padx=(10))

    window.mainloop()

