import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import logging

# Clear the log file
with open('app.log', 'w'):
    pass

# Set up logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class LoggingDemo(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Logging Demo")
        self.geometry("250x250")
        
        # Add buttons
        self.create_button("DEBUG", logging.debug).pack(pady=10)
        self.create_button("INFO", logging.info).pack(pady=10)
        self.create_button("WARNING", logging.warning).pack(pady=10)
        self.create_button("ERROR", logging.error).pack(pady=10)
        self.create_button("CRITICAL", logging.critical).pack(pady=10)
        
    def create_button(self, text, log_func):
        """Creates a button with given text and logging function"""
        return ttk.Button(self, text=text, command=lambda: self.log_message(text, log_func))

    def log_message(self, level, log_func):
        log_func(f"{level} message logged")
        messagebox.showinfo("Logged", f"{level} message has been logged!")

if __name__ == "__main__":
    app = LoggingDemo()
    app.mainloop()