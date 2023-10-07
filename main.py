import os
import platform
import sys
import threading
import time
import webbrowser
from queue import Queue
from tkinter import *
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk
from tkcalendar import DateEntry
from tkfilebrowser import askopendirnames, askopenfilename
from tkmacosx import (
    Button,  # for button colours since doesn't work on macOS (Tkinter issue)
)

from data_analysis.plot import AnalyseSheep
from data_cleaning.data_clean import ProcessData

# from data_cleaning.data_clean_threaded import ProcessData_Threaded
# from data_analysis.plot import start_analysis

clean_data_folder = None
sheep_file = None
analysed_sheep = None
system = platform.system()

global_var_lock = threading.Lock()


# New function for the compiled program
def resource_path(relative_path):
    """Get the correct resource path for PyInstaller"""
    if getattr(sys, 'frozen', False):  # The application is frozen (compiled)
        base_path = sys._MEIPASS
    else:  # Running in a normal Python environment
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def app_root_path():
    """Get the root path of the application (script or packaged executable)"""
    if getattr(sys, 'frozen', False):  # The application is frozen (compiled)
        return os.path.dirname(sys.executable)
    else:  # Running in a normal Python environment
        return os.path.dirname(os.path.abspath(__file__))
# New function for the compiled program


def get_folders(folder_paths):
    folder_paths.append(askopendirnames(title="Select Directory"))
    change_mode("data cleaning")
    files = []
    
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
            
            if system == "Darwin":
                files.append(folder_path.rsplit("/", 1))
            if system == "Windows":
                files.append(folder_path.rsplit("\\", 1)[1])
    change_file(files)
    
    if len(folder_paths) == 1 and folder_paths[0] != ():
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


def clean_files(folder_paths):
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


def unthreaded_clean_files(root, folder_paths):
    process_data = ProcessData()
    
    for tuple in folder_paths:
        for path in tuple:
            if system == "Darwin":
                folder_path_list = path.rsplit("/", 1)
            if system == "Windows":
                folder_path_list = path.rsplit("\\", 1)

            path_to_folder = folder_path_list[0]
            sheep_name = folder_path_list[1]
            
            combined_data = process_data.start_read_data(path, root)
            if len(combined_data) > 0:
                print("Cleaning data in progress")
                cleaned_data = process_data.start_clean_data(root, combined_data)
                combined_data = [] # free memory
                print("Completed data cleaning")
            
                clean_data_folder = path_to_folder+"/"+sheep_name+"_cleaned_data"

                if os.path.isdir(clean_data_folder) == False:
                    os.mkdir(clean_data_folder)

                print("Writing to CSV in progress")
                process_data.start_save_to_csv(cleaned_data,clean_data_folder+"/"+sheep_name+".csv", root)
                print("Completed writing")
                cleaned_data = [] # Free memory
                print(clean_data_folder)

    messagebox.showinfo("Success", "Successfully cleaned selected data files")

def update_status(status_text):
    operation_status.config(text=status_text)


def multithread_reset():
    global folder_paths
    folder_paths = [] # FREE THREADING FILE PATHS
    load_files_button["state"] = NORMAL
    clean_files_button["state"] = DISABLED


def start_analysis(start_date, end_date, start_hour, start_minute, end_hour, end_minute):

    def analysis_thread():
        global analysed_sheep
        global sheep_file
        formatted_start = str(start_date) + " " + start_hour + ":" + start_minute + ":" + "00"
        formatted_end = str(end_date) + " " + end_hour + ":" + end_minute + ":" + "00"
        
        update_status("Please Wait... Plotting data")

        analysed_sheep = AnalyseSheep()
        analysed_sheep.plot_mode = "XYZ"
        current_plot("XYZ")
        
        analysed_sheep.start_analysis(sheep_file, formatted_start, formatted_end)
        update_status("Plotted data successfully")

    if (start_hour != "Hour" and end_hour != "Hour" and start_minute != "Mins" and end_minute != "Mins"):
        threading.Thread(target=analysis_thread).start()
    else:
        messagebox.showinfo("Failure", "Incorrectly chosen DateTime for analysis. Please try again.")
    

def defocus(event):
    event.widget.master.focus_set()
    event.widget.master.selection_clear()


# Selects and holds a sheep csv file from a cleaned sheep directory.
def select_sheep():
    global sheep_file
    global analysed_sheep
    analysed_sheep = None # Remove the existing instance of "AnalyseSheep"
    file_path = askopenfilename(title="Select a cleaned data file", filetypes=[("CSV files", "*.csv")]) # filedialog.askdirectory()
    change_mode("data analysis")
    
    try:
        file_name = os.path.basename(file_path)
        if file_name.startswith("GPS"):
            sheep_file = file_path
            start_analysis_button["state"] = NORMAL
            change_file([file_name]) # Changes the file name display
        else:
            messagebox.showerror("Error", "Invalid directory name, must be a cleaned data file")
            return
    except:
        return


# Updates the intereior content of the current file label.
def change_file(filenames):
    l = len(filenames)
    if l == 0:
        currentFile.config(text="N/A")
    elif l == 1:
        currentFile.config(text=filenames[0])
    elif l > 1 and l < 6:
        s = "["
        for file in filenames:
            s += f"{file}, " 
        s = f"{s[:-2]}]"
        currentFile.config(text=s)
    elif l > 5:
        s = "["
        
        i = 0
        while i < 5:
            s += f"{filenames[i]}, "
            i +=1
            
        s = f"{s}...] + ({l-5}) more."
        currentFile.config(text=s)
    else:
        currentFile.config(text="N/A")
        print("Error: invalid filenames")


# Updates the interior content of the current mode label.
def change_mode(mode):
    modes = ["data cleaning", "data analysis"]
    
    if mode.lower() in modes:
        currentMode.config(text=mode.title())

def current_plot(plot_type):
    types = ["Amplitude", "XYZ"]
    
    if plot_type in types:
        plot_text.config(text=plot_type)

#### DATA ANALYSIS FUNCTIONS
def get_report():
    operation_status.config(text="Please Wait... Saving report to CSV")
    global analysed_sheep
    analysed_sheep.generate_report()
    operation_status.config(text="Saved to CSV successfully")

def plot_amplitude():
    operation_status.config(text="Please Wait... Plotting Amplitude")
    global analysed_sheep
    analysed_sheep.plot_mode = "Amplitude"
    current_plot("Amplitude")
    analysed_sheep.plot_amplitude()
    operation_status.config(text="Plotting Amplitude Completed")


def save_plot_data():
    operation_status.config(text="Please Wait... Saving plot data to CSV")
    global analysed_sheep
    analysed_sheep.write_to_file()
    operation_status.config(text="Saved to CSV successfully")

def export_plot_pdf():
    global analysed_sheep
    operation_status.config(text="Exporting plot to PDF")
    analysed_sheep.export_to_pdf()
    operation_status.config(text="Exported to PDF successfully")



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

    #Data Processing
    Label(menu_frame,  text="Data Processing", bg='#27348b', fg='white', font="Arial 16").grid(row=0, column=0, padx=20, pady=10)
    load_files_button = Button(menu_frame, text="LOAD DIRECTORY", font="Arial 12 bold", background='#fdc300', activebackground='#fdc300', focuscolor='', borderless=True, padx=5, pady=15, command = lambda: get_folders(folder_paths))
    clean_files_button = Button(menu_frame, text="CLEAN DIRECTORY", font="Arial 12 bold", background='#a2c03b', activebackground='#a2c03b', focuscolor='', borderless=True, state=DISABLED, padx=0, pady=15, command = lambda: unthreaded_clean_files(root, folder_paths))
    load_files_button.grid(row=1, column=0, rowspan=2)
    clean_files_button.grid(row=3, rowspan=2, column=0)
    
    #For the separation line
    canvas = Canvas(menu_frame, width=170, height=30, background='#27348b', highlightthickness=0, relief='ridge')
    canvas.create_line(5, 25, 165, 25, width=0, fill='white')
    canvas.grid(row=5, column=0)

    #Data Analysis
    Label(menu_frame,  text="Data Analysis", bg='#27348b', fg='white', font="Arial 16", justify="left").grid(row=6, column=0, pady=5)
    
    Label(menu_frame,  text="Start Date:", bg='#27348b', justify="left", anchor="w", fg='white', font="Arial 12").grid(sticky = W, row=7, column=0)
    start_date = DateEntry(menu_frame, background='#27348b', selectmode='day', date_pattern='yyyy-MM-dd')
    start_date._top_cal.overrideredirect(False)
    start_date.grid(row=7, column=0, padx=(60,0))

    Label(menu_frame,  text="Start Time:", bg='#27348b', fg='white', font="Arial 12").grid(sticky = W, row=9, column=0, pady=(10))

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
    start_hours.grid(row=9, column=0, padx=(0, 0))

    start_minute = StringVar(menu_frame)
    start_minute.set("Mins")
    start_minutes = ttk.Combobox(menu_frame, textvariable=start_minute, state="readonly", values=minutes_list, width=5)
    start_minutes.bind("<FocusIn>", defocus)
    start_minutes.grid(row=9, column=0, padx=(130, 0))

    Label(menu_frame,  text="End Date:", bg='#27348b', justify="left", anchor="w", fg='white', font="Arial 12").grid(sticky = W, row=13, column=0, pady=(20, 0))
    end_date = DateEntry(menu_frame, background='#27348b', selectmode='day', date_pattern='yyyy-MM-dd')
    end_date._top_cal.overrideredirect(False)
    end_date.grid(row=13, column=0, padx=(63, 0), pady=(20, 0))

    Label(menu_frame,  text="End Time:", bg='#27348b', fg='white', font="Arial 12").grid(sticky = W, row=14, column=0, pady=(10, 0))
    end_hour = StringVar(menu_frame)
    end_hour.set("Hour")
    end_hours = ttk.Combobox(menu_frame, textvariable=end_hour, state="readonly", values=hours_list, width=5)
    end_hours.grid(row=14, column=0, pady=(10, 0))

    # colon2 = Label(menu_frame,  text=":", bg='#27348b', fg='white', font="Arial 12")
    # colon2.grid(row=14, column=0, padx=(150, 0))

    end_minute = StringVar(menu_frame)
    end_minute.set("Mins")
    end_minutes = ttk.Combobox(menu_frame, textvariable=end_minute, state="readonly", values=minutes_list, width=5)
    end_minutes.grid(row=14, column=0, padx=(130, 0), pady=(10, 0))

    Label(menu_frame,  text='', bg='#27348b', fg='white', font="Arial 12").grid(sticky = E, row=14, column=0, padx=0, pady=2) #filler label

    #For the separation line
    canvas2 = Canvas(menu_frame, width=170, height=40, background='#27348b', highlightthickness=0, relief='ridge')
    canvas2.create_line(5, 25, 165, 25, width=0, fill='white')
    canvas2.grid(row=15, column=0)

    select_sheep_button = Button(menu_frame, text="SELECT SHEEP", font="Arial 12 bold", background='#fdc300', activebackground='#fdc300', focuscolor='', borderless=True, padx=15, pady=15, command=select_sheep)    
    start_analysis_button = Button(menu_frame, text="START ANALYSIS", font="Arial 12 bold", background='#a2c03b', activebackground='#a2c03b', focuscolor='', borderless=True, state=DISABLED, padx=7, pady=15, command= lambda: start_analysis(start_date.get_date(), end_date.get_date(), start_hours.get(), start_minutes.get(), end_hours.get(), end_minutes.get()))
    select_sheep_button.grid(row=16, column=0, rowspan=2)
    start_analysis_button.grid(row=18, rowspan=2, column=0)
    
    # Change for the compiled program use
    uwa_logo_path = resource_path("UWA-logo-1.png")
    uwa_logo = Image.open(uwa_logo_path)

    img_resized=uwa_logo.resize((220,80)) # new width & height
    my_img=ImageTk.PhotoImage(img_resized)


    l1=Label(menu_frame,image=my_img,background='#27348b')
    l1.grid(column=0, pady=(50, 0))

    #Graph labels and buttons
    Label(graph_frame,  text="Current File(s)", fg='#27348b',bg='white', font="Arial 12 bold").grid(sticky=W, padx=(10), pady=(10, 5), rowspan=2)
    currentFile = Label(graph_frame,  text="N/A", fg='black', bg='white', font="Arial 12")
    currentFile.grid(sticky = W, row=0, column=1, rowspan=2)
    Label(graph_frame,  text="Current Mode", fg='#27348b', bg="white", font="Arial 12 bold").grid(sticky = W, row=2, column=0, padx=(10))
    currentMode = Label(graph_frame,  text="N/A", fg='black', bg="white", font="Arial 12")
    currentMode.grid(sticky = W, row=2, column=1, rowspan=2)
    Label(graph_frame,  text="Current Plot", fg='#27348b', bg="white", font="Arial 12 bold").grid(sticky = W, row=4, column=0, padx=(10), pady=(5))
    plot_text = Label(graph_frame,  text="N/A", fg='black', bg="white", font="Arial 12")
    plot_text.grid(sticky = W, row=3, column=1, rowspan=2)

    operation_status = Label(graph_frame,  text="No operation selected", fg='black', bg="white", font="Arial 12")
    operation_status.grid(sticky = S, row=5, column=0, padx=(10), pady=(5))

    plot_amp = Button(graph_frame, text="PLOT AMPLITUDE SUM", font="Arial 10", background='#27348b', activebackground='#fdc300', fg='white', focuscolor='', borderless=True, padx=5, pady=10,command=plot_amplitude)
    save_analyse_data = Button(graph_frame, text="SAVE PLOT DATA TO FILE", font="Arial 10", background='#27348b', activebackground='#fdc300', fg='white', focuscolor='', borderless=True, padx=5, pady=10,command=save_plot_data)
    export_pdf_button = Button(graph_frame, text="EXPORT TO PDF", font="Arial 10", background='#27348b', activebackground='#fdc300', fg='white', focuscolor='', borderless=True, padx=5, pady=10, command=export_plot_pdf)
    generate_report_button = Button(graph_frame, text="GENERATE REPORT", font="Arial 10", background='#fdc300', activebackground='#a2c03b', focuscolor='', borderless=True, padx=0, pady=10, command=get_report)
    export_pdf_button.place(rely=1.0, relx=1.0, x=-430, y=-10, anchor=SE)
    plot_amp.place(rely=1.0, relx=1.0, x=-260, y=-10, anchor=SE)
    save_analyse_data.place(rely=1.0, relx=1.0, x=-70, y=-10, anchor=SE)
    generate_report_button.place(rely=1.0, relx=1.0, x=-70, y=-60, anchor=SE)

    root.mainloop()