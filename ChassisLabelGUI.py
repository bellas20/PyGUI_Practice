from tkinter import *
import tkinter as tk

# pip install pillow
from PIL import Image, ImageTk

# change just for Github Test

class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.pack(fill=BOTH, expand=1)
                
        load = Image.open("C:/TestFiles5/outputimages/357000stretch.jpg")
        width,height = load.size
        print(width,height)
        numSect = int(width/70)
        print(numSect)

        #resizedload = load.resize((1000,500),Image.ANTIALIAS)
        render = ImageTk.PhotoImage(load)
        img = Label(self, image=render)
        img.image = render
        img.place(x=0, y=0)
        
        #print(render.format, render.size, render.mode)

# second change for Github Test
# third change for github test

root = Tk()
app = Window(root)
root.wm_title("Chassis Object Detection Labeling")
root.geometry("1540x608")
for sect in range(1,numSect)
testButton = tk.Button(  text="Hello, Tkinter", foreground="white", background="black")
testButton.pack()
root.mainloop()