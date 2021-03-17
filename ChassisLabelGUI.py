from tkinter import *
import tkinter

# pip install pillow
from PIL import Image, ImageTk

class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.pack(fill=BOTH, expand=1)
                
        load = Image.open("C:/TestFiles5/outputimages/357000stretch.jpg")
        resizedload = load.resize((1000,500),Image.ANTIALIAS)
        render = ImageTk.PhotoImage(resizedload)
        img = Label(self, image=render)
        img.image = render
        img.place(x=0, y=0)
        
        #print(render.format, render.size, render.mode)

        
root = Tk()
app = Window(root)
root.wm_title("Chassis Object Detection Labeling")
root.geometry("1000x500")
greeting = tkinter.Button(  text="Hello, Tkinter", foreground="white", background="black")
greeting.pack()
root.mainloop()