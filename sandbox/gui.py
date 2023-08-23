from tkinter import *
from tkinter import filedialog

def openFile():
    filepath = filedialog.askopenfilename()
    print(filepath)

window = Tk()
button = Button(text="Open", command=openFile)
button.pack()

window.mainloop()
