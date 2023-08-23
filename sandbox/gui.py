from tkinter import *
from tkinter import filedialog

def openFile():
    filepath = filedialog.askopenfilename()
    print(filepath)

    file = open(filepath, 'r') #reading file 
    print(file.read())
    file.close()


window = Tk()
button = Button(text="Open", command=openFile)
button.pack()

window.mainloop()
