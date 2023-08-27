import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

# Defining functions for each button
def import_data():
    print("TODO: Import data")

def run_analysis():
    print("TODO: Run analysis")

def export_data():
    print("TODO: Export data")

def generate_report():
    print("TODO: Generate report")

# Function to open a file dialog and choose the data path
def choose_file_path():
    file_path = filedialog.askopenfilename(title="Select a Data File", 
                                           filetypes=[("CSV Files", "*.csv"), 
                                                      ("All Files", "*.*")])
    print(f"Selected file: {file_path}")

# Create the main window
root = tk.Tk()
root.title("Sheep Behavior Analysis Program")

# Set the window size to 800x600 pixels
root.geometry("800x600")

# Create buttons and link them to the corresponding functions
btn_import_data = ttk.Button(root, text="Import Data", command=import_data)
btn_run_analysis = ttk.Button(root, text="Run Analysis", command=run_analysis)
btn_export_data = ttk.Button(root, text="Export Data", command=export_data)
btn_generate_report = ttk.Button(root, text="Generate Report", command=generate_report)
btn_import_data.config(command=choose_file_path)

# Create a status bar
status_bar = ttk.Label(root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)

# Place the buttons and status bar on the window
btn_import_data.place(x=100, y=200, width=250, height=50)
btn_run_analysis.place(x=450, y=200, width=250, height=50)
btn_export_data.place(x=100, y=300, width=250, height=50)
btn_generate_report.place(x=450, y=300, width=250, height=50)
status_bar.place(x=0, y=580, width=800, height=20)

# Start the Tkinter event loop
root.mainloop()
