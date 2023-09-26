import os
import sys
import time
import webbrowser
from tkinter import *
import threading
from queue import Queue
from tkinter import filedialog, messagebox, PhotoImage, ttk
from tkmacosx import Button #for button colours since doesn't work on macOS (Tkinter issue)
from tkcalendar import DateEntry
from PIL import Image, ImageTk

from data_cleaning.data_clean import ProcessData

#Global variables
folder_paths = []
path_to_cleaned_data_batch = None
sheep_name = None
current_mode = None
active_labels = []
terminal_window = None

global_var_lock = threading.Lock()

def makeTerminal():
    global terminal_window
    terminal_window = Toplevel()
    terminal_window.title("Terminal Window")
    terminal_window.config(width=300, height=200)

def writeToTerminal():
    text = Text(terminal_window, height=50, width=100)
    text.pack()
    text.insert(END, "Successfully loaded:")
    text.insert(END, folder_paths)

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
            print("folder paths1: ")
            print(folder_paths)
            break  # User clicked Cancel or closed the dialog
        else: 
            # ERROR-HANDLING: Check if only <= 1 file in the folder. Break Selection if True.
            files_in_folder = os.listdir(folder_path)
            print("files in folder:")
            print(files_in_folder)
            if len(files_in_folder) <= 1:
                messagebox.showerror("Error", "Please select a folder containing more than one data file.")
                print("ERROR")
                load_files_button["state"] = NORMAL
                clean_files_button["state"] = DISABLED
                folder_paths.pop()
                break

            # Otherwise: Update GUI and add Path to Array.
            folder_paths.append(folder_path)
            # might not need if we use a terminal window:
            # load_label_batch = Label(graph_frame, text="Successfully loaded: " + folder_path, font=("Helvetica", 18)) 
            # load_label_batch.grid(row=label_count, column=3, sticky="ew")
            # active_labels.append(load_label_batch)

            if len(folder_paths) == 3:
                load_files_button["state"] = DISABLED
                break


            print("folder path: "+ folder_path)
         # Update the label with the selected folder paths
        label_count += 1
    print("folder paths:")
    print(folder_paths)

    if len(folder_paths) == 0:
        load_files_button["state"] = NORMAL
        clean_files_button["state"] = DISABLED
    else: 
        load_files_button["state"] = DISABLED
        clean_files_button["state"] = NORMAL
        makeTerminal()
        writeToTerminal()

def cleanFiles(root):
    print("Data cleaning stuff in here")

def sb1_changed(): # first spinbox
    print("For start hours spinbox")

def sb2_changed(): # second spinbox
    print("For start minutes spinbox")

def sb3_changed(): # first spinbox
    print("For end hours spinbox")

def sb4_changed(): # second spinbox
    print("For end minutes spinbox")

## Application starting point
## Run python3 main.py or python main.py
if __name__ == "__main__":
    root = Tk()
    root.title("Sheep Behavious Analysis")
    root.config(bg="red")
    root.geometry("800x700")
    root.resizable(False, False)

    #Root-> Frames
    menu_frame = Frame(root, width=180, height=700, bg='#27348b')
    menu_frame.grid(row=0, column=0, columnspan=2)
    menu_frame.grid_propagate(0) #stops it resizing

    graph_frame = Frame(root, width=620, height=700, bg='white')
    graph_frame.grid(row=0, column=2)
    graph_frame.grid_propagate(0)

    #Data Processing
    Label(menu_frame,  text="Data Processing", bg='#27348b', fg='white', font="Arial 16").grid(row=0, column=0, padx=25, pady=10)
    load_files_button = Button(menu_frame, text="LOAD DIRECTORY", font="Arial 14 bold", background='#fdc300', activebackground='#fdc300', focuscolor='', borderless=True, padx=5, pady=15, command=getFolders)
    clean_files_button = Button(menu_frame, text="CLEAN DIRECTORY", font="Arial 14 bold", background='#a2c03b', activebackground='#a2c03b', focuscolor='', borderless=True, state=DISABLED, padx=0, pady=15, command = lambda: cleanFiles(root))
    load_files_button.grid(row=1, column=0, rowspan=2)
    clean_files_button.grid(row=3, rowspan=2, column=0)
    
    #For the separation line
    canvas = Canvas(menu_frame, width=170, height=30, background='#27348b', highlightthickness=0, relief='ridge')
    canvas.create_line(5, 25, 165, 25, width=0, fill='white')
    canvas.grid(row=5, column=0)

    #Data Analysis
    Label(menu_frame,  text="Data Analysis", bg='#27348b', fg='white', font="Arial 16").grid(row=6, column=0, padx=25, pady=5)
    
    Label(menu_frame,  text="Start Date", bg='#27348b', justify="left", anchor="w", fg='white', font="Arial 12").grid(sticky = W, row=7, column=0, padx=10, pady=0)
    start_date = date_entry = DateEntry(menu_frame, background='#27348b', selectmode='day')
    date_entry._top_cal.overrideredirect(False)
    date_entry.grid(row=8, column=0)

    Label(menu_frame,  text="Hour", bg='#27348b', fg='white', font="Arial 12").grid(sticky = W, row=9, column=0, padx=0, pady=2)
    Label(menu_frame,  text="Minutes", bg='#27348b', fg='white', font="Arial 12").grid(sticky = E, row=9, column=0, padx=0, pady=2)
    Label(menu_frame,  text='', bg='#27348b', fg='white', font="Arial 12").grid(sticky = E, row=10, column=0, padx=0, pady=3) #filler label
    
    start_hours = Spinbox(menu_frame, text='b1', width=5, from_=00, to=24, command=sb1_changed)
    colon1 = Label(menu_frame,  text=":", bg='#27348b', fg='white', font="Arial 12")
    start_minutes = Spinbox(menu_frame, text='b2', width=5, from_=00, to=59, command=sb2_changed)
    start_hours.place(x=15, y=275)
    colon1.place(x=85, y=275)
    start_minutes.place(x=98, y=275)

    Label(menu_frame,  text="End Date", bg='#27348b', justify="left", anchor="w", fg='white', font="Arial 12").grid(sticky = W, row=11, column=0, padx=10, pady=0)
    end_date = date_entry = DateEntry(menu_frame, background='#27348b', selectmode='day')
    date_entry._top_cal.overrideredirect(False)
    date_entry.grid(row=12, column=0)

    Label(menu_frame,  text="Hour", bg='#27348b', fg='white', font="Arial 12").grid(sticky = W, row=13, column=0, padx=0, pady=2)
    Label(menu_frame,  text="Minutes", bg='#27348b', fg='white', font="Arial 12").grid(sticky = E, row=13, column=0, padx=0, pady=2)
    end_hours = Spinbox(menu_frame, text='b3', width=5, from_=00, to=24, command=sb3_changed)
    colon2 = Label(menu_frame,  text=":", bg='#27348b', fg='white', font="Arial 12")
    end_minutes = Spinbox(menu_frame, text='b4', width=5, from_=00, to=59, command=sb4_changed)
    end_hours.place(x=15, y=380)
    colon2.place(x=85, y=380)
    end_minutes.place(x=98, y=380)
    Label(menu_frame,  text='', bg='#27348b', fg='white', font="Arial 12").grid(sticky = E, row=14, column=0, padx=0, pady=2) #filler label

    #For the separation line
    canvas2 = Canvas(menu_frame, width=170, height=40, background='#27348b', highlightthickness=0, relief='ridge')
    canvas2.create_line(5, 25, 165, 25, width=0, fill='white')
    canvas2.grid(row=15, column=0)

    select_sheep_button = Button(menu_frame, text="SELECT SHEEP", font="Arial 14 bold", background='#fdc300', activebackground='#fdc300', focuscolor='', borderless=True, padx=10, pady=15).grid(row=16, column=0, rowspan=2)
    start_analysis_button = Button(menu_frame, text="START ANALYSIS", font="Arial 14 bold", background='#a2c03b', activebackground='#a2c03b', focuscolor='', borderless=True, padx=5, pady=15).grid(row=18, rowspan=2, column=0)
    
    #Logo
    uwa_logo = Image.open("./UWA-logo-1.png")
    img_resized=uwa_logo.resize((200,100)) # new width & height
    my_img=ImageTk.PhotoImage(img_resized)

    l1=Label(menu_frame,image=my_img,background='#27348b')
    l1.place(rely=1.0, relx=1.0, x=-85, y=-10, anchor=S)

    #Graph labels and buttons
    Label(graph_frame,  text="Current Directory", fg='#27348b', font="Arial 12 bold").grid(row=0, column=0, padx=2, pady=5, rowspan=2)
    Label(graph_frame,  text="", fg='black', font="Arial 12").grid(sticky = W, row=0, column=1, padx=2, pady=5, rowspan=2)
    Label(graph_frame,  text="Current Mode", fg='#27348b', font="Arial 12 bold").grid(sticky = W, row=3, column=0, padx=2)
    Label(graph_frame,  text=current_mode, fg='black', font="Arial 12").grid(sticky = W, row=3, column=1, padx=2, pady=5, rowspan=2)

    export_pdf_button = Button(graph_frame, text="EXPORT TO PDF", font="Arial 12", background='#27348b', activebackground='#fdc300', fg='white', focuscolor='', borderless=True, padx=5, pady=10)
    generate_report_button = Button(graph_frame, text="GENERATE REPORT", font="Arial 12", background='#fdc300', activebackground='#a2c03b', focuscolor='', borderless=True, padx=0, pady=10)
    export_pdf_button.place(x=300, y=500)
    generate_report_button.place(x=450, y=500)

    root.mainloop()


# Get ("Load") folder with sheep files in it
# def getFolder():
#     global folder_path
#     global path_to_folder
#     global sheep_name
    
#     folder_path = filedialog.askdirectory()
#     if not folder_path:
#         return

#     #Get sheep name for clean file name
#     folder_path_list = folder_path.rsplit("/", 1)
#     path_to_folder = folder_path_list[0]
#     sheep_name = folder_path_list[1]

#     # Get a list of files in the selected folder
#     files_in_folder = os.listdir(folder_path)

#     # Check if there is only one file in the folder. Throw Error box if True.
#     if len(files_in_folder) <= 1:
#         messagebox.showerror("Error", "Please select a folder containing more than one data file.")
#         return

#     load_label = Label(graph_frame, text="Successfully loaded: " + folder_path, font=("Helvetica", 18)) 
#     load_label.grid(row=0, column=0, sticky="ew")
#     clean_file_button["state"] = NORMAL

# def cleanFiles(read_pb, clean_pb, write_pb, window):
#     process_data = ProcessData()

#     combined_data = process_data.read_data(folder_path, read_pb, window)

#     print("Cleaning data in progress")
#     cleaned_data = process_data.start_clean_data(clean_pb, window, combined_data)
#     combined_data = [] # free memory
#     print("Completed data cleaning")

#     clean_data_folder = path_to_folder+"/cleaned_data"

#     if os.path.isdir(clean_data_folder) == False:
#         os.mkdir(clean_data_folder)

#     print("Writing to CSV in progress")
#     process_data.start_save_to_csv(cleaned_data,clean_data_folder+"/"+sheep_name+".csv", write_pb, window)
#     print("Completed writing")
#     cleaned_data = [] # Free memory

#     print(clean_data_folder)

#     messagebox.showinfo("Success", "Successfully cleaned selected data files")
#     webbrowser.open('file:///'+clean_data_folder)

    # window = Tk()

    # window.title("Sheep Behaviour Analysis")
    # window.rowconfigure(0, minsize=800, weight=1)
    # window.columnconfigure(1,minsize=800, weight=1)

    # s = ttk.Style()
    # s.theme_use("default")
    # s.configure("TProgressbar", thickness=10)

    #Progress Bars
    # read_pb = ttk.Progressbar(root, style="TProgressbar")
    # clean_pb = ttk.Progressbar(root, mode="indeterminate", style="TProgressbar")
    # write_pb = ttk.Progressbar(root, mode="indeterminate", style="TProgressbar")

    # #Frames
    # menu_frame = Frame(window, width=500, relief=RAISED, bd=2, bg="#27348b")
    # menu_frame.grid(row=0, column=0, sticky="ns")
    # menu_frame.pack_propagate(0)

    # second_frame = Frame(window)
    # second_frame.grid(row=0,column=1)

    # s = ttk.Style()
    # s.theme_use("default")
    # s.configure("TProgressbar", thickness=10)

    # #Progress Bars
    # read_pb = ttk.Progressbar(window, style="TProgressbar")
    # clean_pb = ttk.Progressbar(window, mode="indeterminate", style="TProgressbar")
    # write_pb = ttk.Progressbar(window, mode="indeterminate", style="TProgressbar")

    # #Buttons
    # load_file_button = Button(menu_frame, text='Load Files', command=getFolder) 
    # load_file_button.grid(row=0, column=0, sticky="ew",padx=(10), pady=(5))

    # clean_file_button = Button(menu_frame, text='Clean Files', state=DISABLED, command = lambda: cleanFiles(read_pb, clean_pb, write_pb, window))
    # clean_file_button.grid(row=1, column=0, sticky="ew", padx=(10))

    # window.mainloop()