import os
import platform
import sys
import threading
import time
import webbrowser
from datetime import datetime
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
folder_paths = []
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


def get_folders():
    global folder_paths
    if folder_paths != []:
        folder_paths = []

    folder_paths.append(askopendirnames(title="Select Directory"))
    files = []
    
    for tuple in folder_paths:
        for folder_path in tuple:
            files_in_folder = os.listdir(folder_path)

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
        change_mode("data cleaning")
        clean_files_button["state"] = NORMAL

def unthreaded_clean_files(root):
    global folder_paths
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

                messagebox.showinfo("Success", "Successfully cleaned selected data files")
                webbrowser.open('file:///'+path_to_folder)
            else:
                messagebox.showerror("Error", "Folder does not contain a file with a starting date. Please try again.")
                label_restart()
    label_restart()

def label_restart():
    global folder_paths
    folder_paths = [] #reset folder_paths for next load of folders
    change_file(folder_paths)
    change_mode("N/A")
    load_files_button["state"] = NORMAL
    clean_files_button["state"] = DISABLED

def update_status(status_text):
    operation_status.config(text=status_text)

def start_analysis(start_date, end_date, start_hour, start_minute, end_hour, end_minute):
        global analysed_sheep
        global sheep_file
        formatted_start = str(start_date) + " " + start_hour + ":" + start_minute + ":" + "00"
        formatted_end = str(end_date) + " " + end_hour + ":" + end_minute + ":" + "00"

        if (start_hour != "Hour" and end_hour != "Hour" and start_minute != "Mins" and end_minute != "Mins"):
            # Convert the date-time strings to datetime objects
            date_time1 = datetime.strptime(formatted_start, "%Y-%m-%d %H:%M:%S")
            date_time2 = datetime.strptime(formatted_end, "%Y-%m-%d %H:%M:%S")
        
            # Compare the datetime objects
            if date_time1 >= date_time2:
                messagebox.showinfo("Failure", "The first date is not before or the same as the second date. Please try again.")
            else:
                update_status("Please Wait... Plotting data")
                plot_amp["state"] = NORMAL
                save_analyse_data["state"] = NORMAL
                export_pdf_button["state"] = NORMAL
                generate_report_button["state"] = NORMAL
                plot_accelerometer_button["state"] = NORMAL

                analysed_sheep = AnalyseSheep()
                analysed_sheep.plot_mode = "XYZ"
                current_plot("XYZ")
            
                analysed_sheep.start_analysis(sheep_file, formatted_start, formatted_end)
                update_status("Plotted data successfully")
                avg_hertz.config(text=analysed_sheep.avg_hertz)
        else:
            messagebox.showinfo("Failure", "Incorrectly chosen DateTime for analysis. Please try again.")

#Calendar defocus so it doesn't highlight the calendar when pressed
def defocus(event):
    event.widget.master.focus_set()
    event.widget.master.selection_clear()

# Selects and holds a sheep csv file from a cleaned sheep directory.
def select_sheep():
    global sheep_file
    global analysed_sheep
    analysed_sheep = None # Remove the existing instance of "AnalyseSheep"
    file_path = None
    file_path = askopenfilename(title="Select a cleaned data file", filetypes=[("CSV files", "*.csv")]) # filedialog.askdirectory()
    if len(file_path) != 0:
        try:
            file_name = os.path.basename(file_path)
            if file_name.startswith("GPS"):
                sheep_file = file_path
                start_analysis_button["state"] = NORMAL
                change_file([file_name]) # Changes the file name display
                change_mode("data analysis")
            else:
                messagebox.showerror("Error", "Invalid directory name, must be a cleaned data file")
                return
        except:
            return
    else:
        return

# Updates the interior content of the current file label.
def change_file(filenames):
    l = len(filenames)
    if l == 0:
        current_file.config(text="N/A")
    elif l == 1:
        current_file.config(text=filenames[0])
    elif l > 1 and l < 4:
        s = ""
        for file in filenames:
            s += f"{file[1]}, " 
        s = f"{s[:-2]}"
        current_file.config(text=s)
    elif l > 3:
        s = ""
        s = f"{filenames[0][1]}... + ({l-1}) more."
        current_file.config(text=s)
    else:
        current_file.config(text="N/A")
        print("Error: invalid filenames")


# Updates the interior content of the current mode label.
def change_mode(mode):
    modes = ["data cleaning", "data analysis", "n/a"]
    
    if mode.lower() in modes:
        current_mode.config(text=mode.title())

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

def export_plot():
    global analysed_sheep
    operation_status.config(text="Exporting plot")
    analysed_sheep.export_plot()
    operation_status.config(text="Exported successfully")


def plot_accel():
    global analysed_sheep
    update_status("Please Wait... Plotting data")
    current_plot("XYZ")
    analysed_sheep.plot()
    operation_status.config(text="Plotting Accelerometer Completed")

## Application starting point
## Run python3 main.py or python main.py
if __name__ == "__main__":
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
    load_files_button = Button(menu_frame, text="LOAD DIRECTORY", font="Arial 12 bold", background='#fdc300', activebackground='#fdc300', focuscolor='', borderless=True, padx=5, pady=15, command=get_folders)
    clean_files_button = Button(menu_frame, text="CLEAN DIRECTORY", font="Arial 12 bold", background='#a2c03b', activebackground='#a2c03b', focuscolor='', borderless=True, state=DISABLED, padx=0, pady=15, command = lambda: unthreaded_clean_files(root))
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
    current_file = Label(graph_frame,  text="N/A", fg='black', bg='white', font="Arial 12")
    current_file.grid(sticky = W, row=0, column=1, rowspan=2)
    Label(graph_frame,  text="Current Mode", fg='#27348b', bg="white", font="Arial 12 bold").grid(sticky = W, row=2, column=0, padx=(10))
    current_mode = Label(graph_frame,  text="N/A", fg='black', bg="white", font="Arial 12")
    current_mode.grid(sticky = W, row=2, column=1, rowspan=2)
    Label(graph_frame,  text="Current Plot", fg='#27348b', bg="white", font="Arial 12 bold").grid(sticky = W, row=4, column=0, padx=(10), pady=(5))
    plot_text = Label(graph_frame,  text="N/A", fg='black', bg="white", font="Arial 12")
    plot_text.grid(sticky = W, row=3, column=1, rowspan=2)

    Label(graph_frame,  text="Average Hertz", fg='#27348b',bg='white', font="Arial 12 bold").grid(sticky=W, padx=(10), rowspan=2)
    avg_hertz = Label(graph_frame,  text="N/A", fg='black', bg="white", font="Arial 12")
    avg_hertz.grid(sticky = W, row=6, column=1)

    operation_status = Label(graph_frame,  text="No operation selected", fg='black', bg="white", font="Arial 12")
    operation_status.grid(sticky = S, row=7, column=0, padx=(10), pady=(5))

    plot_amp = Button(graph_frame, text="PLOT AMPLITUDE SUM", font="Arial 10", background='#27348b', activebackground='#fdc300', fg='white', focuscolor='', state=DISABLED,  borderless=True, padx=5, pady=10,command=plot_amplitude)
    save_analyse_data = Button(graph_frame, text="SAVE PLOT DATA TO FILE", font="Arial 10", background='#27348b', activebackground='#fdc300', fg='white', focuscolor='',  state=DISABLED, borderless=True, padx=5, pady=10,command=save_plot_data)
    export_pdf_button = Button(graph_frame, text="EXPORT PLOT", font="Arial 10", background='#27348b', activebackground='#fdc300', fg='white', focuscolor='', state=DISABLED, borderless=True, padx=5, pady=10, command=export_plot)
    generate_report_button = Button(graph_frame, text="GENERATE REPORT", font="Arial 10", background='#fdc300', activebackground='#a2c03b', focuscolor='', state=DISABLED, borderless=True, padx=0, pady=10, command=get_report)
    plot_accelerometer_button = Button(graph_frame, text="PLOT ACCELEROMETER", font="Arial 10", background='#27348b', activebackground='#a2c03b', focuscolor='', state=DISABLED, borderless=True, padx=0, pady=10, command=plot_accel)
    export_pdf_button.place(rely=1.0, relx=1.0, x=-410, y=-10, anchor=SE)
    plot_amp.place(rely=1.0, relx=1.0, x=-240, y=-10, anchor=SE)
    save_analyse_data.place(rely=1.0, relx=1.0, x=-220, y=-60, anchor=SE)
    generate_report_button.place(rely=1.0, relx=1.0, x=-70, y=-60, anchor=SE)
    plot_accelerometer_button.place(rely=1.0, relx=1.0, x=-70, y=-10, anchor=SE)

    root.mainloop()