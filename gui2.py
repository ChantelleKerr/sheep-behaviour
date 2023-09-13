from tkinter import *
from tkinter import filedialog
import sys

filepaths = None
cleanedFile = None

def openFiles():
    global filepaths
    fps = filedialog.askopenfilenames(filetypes=[("CSV Files", "*.csv")])
    if not fps:
        return

    filepaths = list(fps)

    label = Label(second_frame, text="Successfully loaded:", font=("Helvetica", 18)) 
    label.grid(row=0, column=0, sticky="ew")

    increment = 0
    for filepath in filepaths:
        try:
            label = Label(second_frame, text=filepath) 
            label.grid(row=1+increment, column=0, sticky="ew")
            increment = increment+1
            clean_file_button["state"] = NORMAL
        except:
            print("Could not open file:", filepath)
            sys.exit()

def cleanFiles():
    global cleanedFile

    for filepath in filepaths:
        try:
            print(filepath)
            file = open(filepath, 'r') #Reading file

            # DO SOMETHING WITH OPENED FILE
            ###############################
            cleanedFile = "Hello World"
        except:
            sys.exit()

    # Get the directory of the selected files:
    directory = filepaths[0].rsplit("/", 1)

    clean_filename = directory[0]+"/cleanfile.txt"
    print(clean_filename)
    f=open(clean_filename,'w') 
    f.write(cleanedFile) 
    f.close()

window = Tk()

window.title("Sheep Behaviour Analysis")
window.rowconfigure(0, minsize=800, weight=1)
window.columnconfigure(1,minsize=800, weight=1)

menu_frame = Frame(window, relief=RAISED, bd=2, bg="gray98")
menu_frame.grid(row=0, column=0, sticky="ns")

second_frame = Frame(window)
second_frame.grid(row=0,column=1)

load_file_button = Button(menu_frame, text='Load Files', command=openFiles) 
load_file_button.grid(row=0, column=0, sticky="ew",padx=(5), pady=(5))

clean_file_button = Button(menu_frame, text='Clean Files', state=DISABLED, command=cleanFiles)
clean_file_button.grid(row=1, column=0, sticky="ew", padx=(10))

window.mainloop()


read_time = time.time()
    print("Reading file in progress")
    combined_data = process_data.read_data(folder_path)
    read_end_time = time.time()
    print("Completed file read")
   
    print("Cleaning data in progress")
    start_clean_time = time.time()
    cleaned_data = process_data.clean_data(combined_data)
    end_clean_time = time.time()
    print("Completed data cleaning")
    
    print("Writing to CSV in progress")
    start_write_time = time.time()
    process_data.save_to_csv(cleaned_data, "test_data/sheep1/cleaned.csv")
    end_write_time = time.time()
    print("Completed writing")


    end_time = time.time()
    
    total_read_time = read_end_time - read_time
    total_clean_time = end_clean_time - start_clean_time 
    total_write_time = end_write_time - start_write_time
    elapsed_time = end_time - start_time

    print(f"Read time: {total_read_time} seconds")
    print(f"Clean time: {total_clean_time} seconds")
    print(f"Write time: {total_write_time} seconds")
    print(f"Total Elapsed time: {elapsed_time} seconds")