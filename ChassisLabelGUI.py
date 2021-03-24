from tkinter import *
import tkinter as tk
import os

# pip install pillow
from PIL import Image, ImageTk
import time

#def PickLabel(section):
#    print("popup screen for section: " + str(section))
gChassisNum = 357100
gRobotNum = "R1"
gCurrentSect = 0
gLboxSelect = 0
# output mode is 0 for text file or 1 for database output
gOutputMode = 0
if (gOutputMode==0):
    outFileName = "chassisLabeling.txt"
    if os.path.isfile(outFileName):
        outF = open(outFileName,"a")
        #outF.write("\n")
    else:
        outF = open(outFileName,"a")

def assignSectNum(sect):
    global gCurrentSect
    gCurrentSect = sect
    print(gCurrentSect)
    outbox.delete(1.0,1.15)
    outbox.delete(3.0,END)
    outbox.insert(1.0,"Section: " + str(sect)+"\n")

def LboxSelect(event):
    global gLboxSelect
    outbox.delete(2.0,2.15)
    outbox.delete(3.0,END)
    outbox.insert(2.0,Lbox.get(ANCHOR)+"\n")
    gLboxSelect=(Lbox.get(ANCHOR))

def SavetoDB():
    global gChassisNum
    global gRobotNum
    global gCurrentSect
    global gLboxSelect
    if (gCurrentSect>0):
        messbox.delete(1.0,END)
        if (gOutputMode==0):
            outText = str(gChassisNum)+","+gRobotNum+","+str(gCurrentSect)+","+gLboxSelect+"\n"
            print (outText)
            outF.write(outText)
            messbox.insert(1.0,"Saved to Textfile\n")
        else:    
            messbox.insert(1.0,"Saved to Database\n")
            print(gChassisNum)
            print(gCurrentSect)
            print(gLboxSelect)
    else:
        messbox.delete(1.0,4.15)
        messbox.insert(1.0,"Data not Complete\n")
        #print(type(gCurrentSect))
        print(gCurrentSect)
        print(gLboxSelect)

def ClearTextBox():
    global gCurrentSect
    gCurrentSect = 0
    outbox.delete(1.0,END)
    messbox.delete(1.0,END)

def CloseFile():
    outF.close()

sectWidth = 70               
load = Image.open("C:/TestFiles5/outputimages/357000stretch.jpg")
width,height = load.size
aspRatio=width/height
print(width,height)
numSect = int(width/sectWidth)
print(numSect)
newSectWidth = 1000//numSect
newImgWidth = newSectWidth*numSect
newImgHeight = newImgWidth//int(aspRatio)
resizedload = load.resize((newImgWidth,newImgHeight),Image.ANTIALIAS)

root = Tk()
root.title("Chassis Object Detection Labeling")
screenSizeStr = str(newImgWidth+150) + "x" + str(newImgHeight+40)
root.geometry(screenSizeStr)
buttons = []
for sect in range(0,numSect):
    buttons.append(tk.Button(text=sect+1,padx=newImgWidth//80, pady=20, bd=3,fg="black", \
        bg="grey",activebackground="yellow",relief=RAISED, \
        command = lambda arg1=sect+1: assignSectNum(arg1)))
    buttons[sect].place(x=sect*newSectWidth,y=newImgHeight)

print(len(buttons))
render = ImageTk.PhotoImage(resizedload)

img = Label(root, image=render)
img.image = render
img.place(x=0,y=0)

Lbox = Listbox(root, selectmode=SINGLE)
Lbox.insert(1, "BackRearAxle")
Lbox.insert(2, "FrontRearAxle")
Lbox.insert(3, "BackRearAxle3")
Lbox.insert(4, "CenterRearAxle3")
Lbox.insert(5, "FrontRearAxle3")
Lbox.insert(6, "FuelTankBrkt")

Lbox.place(x=newImgWidth,y=0)
Lbox.bind('<<ListboxSelect>>',LboxSelect)

outbox=Text(root, height=4, width=18)
outbox.place(x=newImgWidth,y=newImgHeight//2)

messbox=Text(root, height=4,width=18)
messbox.place(x=newImgWidth,y=newImgHeight*3//4)
messText = "Message Box\n"
messbox.insert(END,messText)

if (gOutputMode==1):
    saveButton = tk.Button(text="Save to Database", activebackground="yellow", command = SavetoDB)
    saveButton.place(x=newImgWidth+15,y=newImgHeight//2-30)
else:
    saveButton = tk.Button(text="Save to Text File", activebackground="yellow", command = SavetoDB)
    saveButton.place(x=newImgWidth+15,y=newImgHeight//2-30)
    closeFileButton = tk.Button(text="Close Text File", activebackground="yellow", command = CloseFile)
    closeFileButton.place(x=newImgWidth+15,y=newImgHeight+13)    

clearButton = tk.Button(text="Clear Data", activebackground="yellow", command = ClearTextBox)
clearButton.place(x=newImgWidth+15,y=newImgHeight-15)

root.mainloop()