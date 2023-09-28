import os
import time
import webbrowser
import ttk
from tkinter import *
import threading
from queue import Queue
from tkinter import filedialog, messagebox
from tkmacosx import Button #for button colours since doesn't work on macOS (Tkinter issue)
from tkcalendar import DateEntry
from PIL import Image, ImageTk

from data_cleaning.data_clean import ProcessData
from data_analysis.plot import PlotData
from tkfilebrowser import askopendirnames, askopenfilename

# from data_cleaning.data_clean_threaded import ProcessData_Threaded
# from data_analysis.plot import start_analysis

clean_data_folder = None
sheep_file = None

global_var_lock = threading.Lock()


def getFolders(folder_paths):
    folder_paths.append(askopendirnames())
    print(folder_paths)

    for tuple in folder_paths:
        for folder_path in tuple:
            files_in_folder = os.listdir(folder_path)
            print("Files in Folder:")
            print(files_in_folder)

            #Checking that selected folders contain more than 1 file 
            if len(files_in_folder) <= 1:
                messagebox.showerror("Error", "Folder: "+folder_path+" contains less than 2 files. Please select a folder which contains more than one data file.")
                folder_paths.pop()
                break

    if len(folder_paths) == 1:
        load_files_button["state"] = DISABLED
        clean_files_button["state"] = NORMAL
    return folder_paths


# MULTITHREADED: Batch Cleaning
def clean_files_thread(folder_path):
    global_var_lock.acquire()
    global clean_data_folder
    try:
        # process_data = ProcessData_Threaded()
        # combined_data = process_data.read_data(folder_path)

        #Get sheep name for clean file name
        folder_path_list = folder_path.rsplit("/", 1)
        path_to_folder = folder_path_list[0]
        sheep_name = folder_path_list[1]

        print("Currently cleaning folder: "+sheep_name)
        # cleaned_data = process_data.start_clean_data(combined_data)
        combined_data = []  # Free memory
        print("Completed cleaning for folder "+sheep_name)

        clean_data_folder = path_to_folder + "/cleaned_data_batch"
        if not os.path.isdir(clean_data_folder):
            os.mkdir(clean_data_folder)

        print("Currently writing CSV for folder: "+sheep_name)
        # process_data.start_save_to_csv(cleaned_data, clean_data_folder + "/" + sheep_name + ".csv")
        print("Completed writing CSV for folder: "+sheep_name)
        cleaned_data = []  # Free memory
    finally:
    # Release the lock after modifying the array
        global_var_lock.release()


def cleanFiles(folder_paths):
    global clean_data_folder

    print("Folder paths in clean file:")
    print(folder_paths)

    threads = []
    start_time = time.time()

    for tuple in folder_paths:
        for folder_path in tuple:
            thread = threading.Thread(target=clean_files_thread, args=(folder_path,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed Threading Time: {elapsed_time} seconds")

    messagebox.showinfo("Success", "Successfully cleaned selected data folders.")
    print(clean_data_folder)
    webbrowser.open('file:///'+ clean_data_folder)
    multithread_reset()


def unthreaded_clean_files(read_pb, clean_pb, write_pb, root, folder_paths):
    process_data = ProcessData()
    
    for tuple in folder_paths:
        for path in tuple:
            folder_path_list = path.rsplit("\\", 1)
            path_to_folder = folder_path_list[0]
            sheep_name = folder_path_list[1]
            
            combined_data = process_data.read_data(path, read_pb, root)
            if len(combined_data) > 0:
                print("Cleaning data in progress")
                cleaned_data = process_data.start_clean_data(clean_pb, root, combined_data)
                combined_data = [] # free memory
                print("Completed data cleaning")
            
                clean_data_folder = path_to_folder+"/"+sheep_name+"_cleaned_data"

                if os.path.isdir(clean_data_folder) == False:
                    os.mkdir(clean_data_folder)

                print("Writing to CSV in progress")
                process_data.start_save_to_csv(cleaned_data,clean_data_folder+"/"+sheep_name+".csv", write_pb, root)
                print("Completed writing")
                cleaned_data = [] # Free memory

                print(clean_data_folder)

    messagebox.showinfo("Success", "Successfully cleaned selected data files")


def multithread_reset():
    global folder_paths
    folder_paths = [] # FREE THREADING FILE PATHS
    load_files_button["state"] = NORMAL
    clean_files_button["state"] = DISABLED


def startAnalysis(start_date, end_date, start_hour, start_minute, end_hour, end_minute):
    plot_data = PlotData()
    global sheep_file
    
    if (start_hour != "Hour" and end_hour != "Hour" and start_minute != "Mins" and end_minute != "Mins"):
        formatted_start = str(start_date) + " " + start_hour + ":" + start_minute + ":" + "00"
        formatted_end = str(end_date) + " " + end_hour + ":" + end_minute + ":" + "00"
        print(formatted_start)
        print(formatted_end)
        print(sheep_file)
        
        plot_data.start_analysis(sheep_file, formatted_start, formatted_end)

    else:
        messagebox.showinfo("Failure", "Incorrectly chosen DateTime for analysis. Please try again.")
    

def defocus(event):
    event.widget.master.focus_set()
    event.widget.master.selection_clear()


# Selects and holds a sheep csv file from a cleaned sheep directory.
def selectSheep():
    global sheep_file
    folder_path = filedialog.askdirectory()
    
    try:
        file_name = folder_path.rsplit("/", 1)[1]
        if file_name.split('_', 1)[1] == "cleaned_data":
            sheep = os.listdir(folder_path)[0]
            if sheep.endswith(".csv"):
                sheep_file = folder_path + "/" + sheep
                start_analysis_button["state"] = NORMAL
            else:
                messagebox.showerror("Error", "Sheep file is not a csv")
                return
        else:
            messagebox.showerror("Error", "Invalid directory name, must be a cleaned data file")
            return
    except:
        messagebox.showerror("Error", "Invalid directory name, must be a cleaned data file")
        return
    
    messagebox.showinfo("Success", "Successfully selected: " + sheep_file)

## Application starting point
## Run python3 main.py or python main.py
if __name__ == "__main__":
    folder_paths = []

    root = Tk()
    root.title("Sheep Behavious Analysis")
    root.config(bg="red")
    root.geometry("800x700")
    root.resizable(False, False)

    #Root-> Frames
    menu_frame = Frame(root, width=220, height=700, bg='#27348b')
    menu_frame.grid(row=0, column=0, columnspan=2)
    menu_frame.grid_propagate(0) #stops it resizing

    graph_frame = Frame(root, width=620, height=700, bg='white')
    graph_frame.grid(row=0, column=2)
    graph_frame.grid_propagate(0)
    
    # Progress Bars
    read_pb = ttk.Progressbar(root, style="TProgressbar")
    clean_pb = ttk.Progressbar(root, mode="indeterminate", style="TProgressbar")
    write_pb = ttk.Progressbar(root, mode="indeterminate", style="TProgressbar")


    #Data Processing
    Label(menu_frame,  text="Data Processing", bg='#27348b', fg='white', font="Arial 16").grid(row=0, column=0, padx=25, pady=10)
    load_files_button = Button(menu_frame, text="LOAD DIRECTORY", font="Arial 14 bold", background='#fdc300', activebackground='#fdc300', focuscolor='', borderless=True, padx=5, pady=15, command = lambda: getFolders(folder_paths))
    clean_files_button = Button(menu_frame, text="CLEAN DIRECTORY", font="Arial 14 bold", background='#a2c03b', activebackground='#a2c03b', focuscolor='', borderless=True, state=DISABLED, padx=0, pady=15, command = lambda: unthreaded_clean_files(read_pb, clean_pb, write_pb, root, folder_paths))
    load_files_button.grid(row=1, column=0, rowspan=2)
    clean_files_button.grid(row=3, rowspan=2, column=0)
    
    #For the separation line
    canvas = Canvas(menu_frame, width=170, height=30, background='#27348b', highlightthickness=0, relief='ridge')
    canvas.create_line(5, 25, 165, 25, width=0, fill='white')
    canvas.grid(row=5, column=0)

    #Data Analysis
    Label(menu_frame,  text="Data Analysis", bg='#27348b', fg='white', font="Arial 16").grid(row=6, column=0, padx=25, pady=5)
    
    Label(menu_frame,  text="Start Date", bg='#27348b', justify="left", anchor="w", fg='white', font="Arial 12").grid(sticky = W, row=7, column=0, padx=10, pady=0)
    start_date = DateEntry(menu_frame, background='#27348b', selectmode='day', date_pattern='yyyy-MM-dd')
    start_date._top_cal.overrideredirect(False)
    start_date.grid(row=8, column=0)

    Label(menu_frame,  text="Start Time", bg='#27348b', fg='white', font="Arial 12").grid(sticky = W, row=9, column=0, padx=0, pady=2)
    Label(menu_frame,  text='', bg='#27348b', fg='white', font="Arial 12").grid(sticky = E, row=10, column=0, padx=0, pady=3) #filler label
    
    hours_list = []
    minutes_list = []
    for i in range(24):
        if i < 10:
            hours_list.append('0'+str(i))
        else:
            hours_list.append(str(i))
    for i in range(60):
        if i < 10:
            minutes_list.append('0'+str(i))
        else:
            minutes_list.append(str(i))

    start_hour = StringVar(menu_frame)
    start_hour.set("Hour")
    start_hours = ttk.Combobox(menu_frame, textvariable=start_hour, state="readonly", values=hours_list, width=5)
    start_hours.bind("<FocusIn>", defocus)
    start_hours.place(x=15, y=275)
    
    colon1 = Label(menu_frame,  text=":", bg='#27348b', fg='white', font="Arial 12")
    colon1.place(x=86, y=275)

    start_minute = StringVar(menu_frame)
    start_minute.set("Mins")
    start_minutes = ttk.Combobox(menu_frame, textvariable=start_minute, state="readonly", values=minutes_list, width=5)
    start_minutes.bind("<FocusIn>", defocus)
    start_minutes.place(x=98, y=275)

    Label(menu_frame,  text="End Date", bg='#27348b', justify="left", anchor="w", fg='white', font="Arial 12").grid(sticky = W, row=11, column=0, padx=10, pady=0)
    end_date = DateEntry(menu_frame, background='#27348b', selectmode='day', date_pattern='yyyy-MM-dd')
    end_date._top_cal.overrideredirect(False)
    end_date.grid(row=12, column=0)

    Label(menu_frame,  text="End Time", bg='#27348b', fg='white', font="Arial 12").grid(sticky = W, row=13, column=0, padx=0, pady=2)
    end_hour = StringVar(menu_frame)
    end_hour.set("Hour")
    end_hours = ttk.Combobox(menu_frame, textvariable=end_hour, state="readonly", values=hours_list, width=5)
    end_hours.place(x=15, y=380)

    colon2 = Label(menu_frame,  text=":", bg='#27348b', fg='white', font="Arial 12")
    colon2.place(x=86, y=380)

    end_minute = StringVar(menu_frame)
    end_minute.set("Mins")
    end_minutes = ttk.Combobox(menu_frame, textvariable=end_minute, state="readonly", values=minutes_list, width=5)
    end_minutes.place(x=98, y=380)

    Label(menu_frame,  text='', bg='#27348b', fg='white', font="Arial 12").grid(sticky = E, row=14, column=0, padx=0, pady=2) #filler label

    #For the separation line
    canvas2 = Canvas(menu_frame, width=170, height=40, background='#27348b', highlightthickness=0, relief='ridge')
    canvas2.create_line(5, 25, 165, 25, width=0, fill='white')
    canvas2.grid(row=15, column=0)

    select_sheep_button = Button(menu_frame, text="SELECT SHEEP", font="Arial 14 bold", background='#fdc300', activebackground='#fdc300', focuscolor='', borderless=True, padx=10, pady=15, command=selectSheep)    
    start_analysis_button = Button(menu_frame, text="START ANALYSIS", font="Arial 14 bold", background='#a2c03b', activebackground='#a2c03b', focuscolor='', borderless=True, state=DISABLED, padx=5, pady=15, command= lambda: startAnalysis(start_date.get_date(), end_date.get_date(), start_hours.get(), start_minutes.get(), end_hours.get(), end_minutes.get()))
    select_sheep_button.grid(row=16, column=0, rowspan=2)
    start_analysis_button.grid(row=18, rowspan=2, column=0)
    
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
    Label(graph_frame,  text="", fg='black', font="Arial 12").grid(sticky = W, row=3, column=1, padx=2, pady=5, rowspan=2)

    export_pdf_button = Button(graph_frame, text="EXPORT TO PDF", font="Arial 12", background='#27348b', activebackground='#fdc300', fg='white', focuscolor='', borderless=True, padx=5, pady=10)
    generate_report_button = Button(graph_frame, text="GENERATE REPORT", font="Arial 12", background='#fdc300', activebackground='#a2c03b', focuscolor='', borderless=True, padx=0, pady=10)
    export_pdf_button.place(x=300, y=500)
    generate_report_button.place(x=450, y=500)

    root.mainloop()