from tkinter import *
from tkinter import filedialog
import sys

def openFile():
    filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not filepath:
        return

    try: 
        file = open(filepath, 'r') #reading file 
        cleanFileButton(file)

        file.close()
    except:
        print("Could not open file:", filepath)
        sys.exit()

def cleanFileButton(file):
    clean_file_button["state"] = NORMAL
    # reading from the file
    print(file.read())

window = Tk()

window.title("Sheep Behaviour Analysis")
window.rowconfigure(0, minsize=800, weight=1)
window.columnconfigure(1,minsize=800, weight=1)

menu_frame = Frame(window, relief=RAISED, bd=2, bg="gray98")
menu_frame.grid(row=0, column=0, sticky="ns")

load_file_button = Button(menu_frame, text='Load File', command=openFile) 
load_file_button.grid(row=0, column=0, sticky="ew",padx=(5), pady=(5))

clean_file_button = Button(menu_frame, text='Clean File', state=DISABLED, command=cleanFileButton)
clean_file_button.grid(row=1, column=0, sticky="ew", padx=(10))

window.mainloop()
