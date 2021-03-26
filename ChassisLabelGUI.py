# pylint: disable=W0614
from tkinter import *
import tkinter as tk
import os
from pathlib import Path
import atexit

from PIL import Image, ImageTk

#Define Globals
gCurrentFileIndex = 0

gRobotNum = "R1"
gCurrentSect = 0
gLboxSelect = 0
newImgWidth = 0
newImgHeight = 0

# List all files in directory using pathlib
# Define directory and image file type here
# assumption is that file name is a 6 digit chassis number
jpgList = []
jpgListName = []
basepath = Path('C:/TestFiles5/outputimages/')
files_in_basepath = (entry for entry in basepath.iterdir() if entry.is_file())
for item in files_in_basepath:
    if (item.name.endswith('.jpg')):
        jpgList.append(item)
        print(item.name)
        jpgListName.append(item.name[:6:])

#Global Chassis Number = Image Number
gChassisNum = jpgListName[gCurrentFileIndex]

# Set output mode - 0 for text file or 1 for database output
gOutputMode = 0
if (gOutputMode==0):
    outFileName = "chassisLabeling.txt"
    if os.path.isfile(outFileName):
        outF = open(outFileName,"a")
        #outF.write("\n")
    else:
        outF = open(outFileName,"a")

#Function Definitions
def assignSectNum(sect):
    global gCurrentSect
    gCurrentSect = sect
    print(gCurrentSect)
    outbox.delete(1.0,END)
    outbox.insert(1.0,"Section: " + str(sect)+"\n")
    messbox.delete(1.0,END)

def LboxSelect(event):
    global gLboxSelect
    labelOutBox.delete(1.0,END)
    labelOutBox.insert(1.0,Lbox.get(ANCHOR)+"\n")
    gLboxSelect=(Lbox.get(ANCHOR))

def SavetoDB():
    #global gChassisNum
    #global gRobotNum
    #global gCurrentSect
    #global gLboxSelect
    if (gCurrentSect>0):
        messbox.delete(1.0,END)
        if (gOutputMode==0):
            outText = str(gChassisNum)+","+gRobotNum+","+str(gCurrentSect)+","+gLboxSelect+"\n"
            #print (outText)
            outF.write(outText)
            messbox.insert(1.0,"Saved to Textfile\n")
        else:    
            messbox.insert(1.0,"Saved to Database\n")
            #print(gChassisNum)
            #print(gCurrentSect)
            #print(gLboxSelect)
    else:
        messbox.delete(1.0,4.15)
        messbox.insert(1.0,"Data not Complete\n")
        #print(type(gCurrentSect))
        #print(gCurrentSect)
        #print(gLboxSelect)

def ClearTextBox():
    global gCurrentSect
    gCurrentSect = 0
    outbox.delete(1.0,END)
    labelOutBox.delete(1.0,END)

def CloseFile():
    outF.close()
    print("Output File Closed")

def NextImg():
    global gCurrentFileIndex
    global gChassisNum
    LoadImage.img.destroy()
    for button in LoadImage.buttons:
        button.destroy()
    if (gCurrentFileIndex<(len(jpgListName)-1)):
        gCurrentFileIndex+=1
    gChassisNum = jpgListName[gCurrentFileIndex]
    print (gChassisNum)
    chsTextBox.delete(1.0,END)
    mess='Image: '+str(gChassisNum)+'\n'
    chsTextBox.insert(1.0,mess)
    LoadImage()

def PrevImg():
    global gCurrentFileIndex
    global gChassisNum
    LoadImage.img.destroy()
    for button in LoadImage.buttons:
        button.destroy()
    if (gCurrentFileIndex>0):
        gCurrentFileIndex-=1
    gChassisNum = jpgListName[gCurrentFileIndex]
    print (gChassisNum)
    chsTextBox.delete(1.0,END)
    mess='Image: '+str(gChassisNum)+'\n'
    chsTextBox.insert(1.0,mess)
    LoadImage()

#Load Image
def LoadImage():
    global newImgHeight
    global newImgWidth
    sectWidth = 70 
    load = Image.open(jpgList[gCurrentFileIndex])
    width,height = load.size
    aspRatio=width/height
    print(width,height)
    numSect = int(width/sectWidth)
    print(numSect)
    newSectWidth = 1000//numSect
    newImgWidth = newSectWidth*numSect
    newImgHeight = newImgWidth//int(aspRatio)
    resizedload = load.resize((newImgWidth,newImgHeight),Image.ANTIALIAS)
    render = ImageTk.PhotoImage(resizedload)
    LoadImage.img = Label(root, image=render)
    LoadImage.img.image = render
    LoadImage.img.place(x=0,y=0)
    LoadImage.buttons = []
    for sect in range(0,numSect):
        LoadImage.buttons.append(tk.Button(text=sect+1,padx=newImgWidth//80, pady=20, bd=3,fg="black", \
            bg="grey",activebackground="yellow",relief=RAISED, \
            command = lambda arg1=sect+1: assignSectNum(arg1)))
        LoadImage.buttons[sect].place(x=sect*newSectWidth,y=newImgHeight)
        print(len(LoadImage.buttons))

root = Tk()
root.title("Chassis Object Detection Labeling")
screenSizeStr = str(1150) + "x" + str(600)
root.geometry(screenSizeStr)

#Initial Image Load
LoadImage()

#define and place widgets
#ListBox for Labels
Lbox = Listbox(root, selectmode=SINGLE)
Lbox.insert(1, "BackRearAxle")
Lbox.insert(2, "FrontRearAxle")
Lbox.insert(3, "BackRearAxle3")
Lbox.insert(4, "CenterRearAxle3")
Lbox.insert(5, "FrontRearAxle3")
Lbox.insert(6, "FuelTankBrkt")

Lbox.place(x=newImgWidth,y=0)
Lbox.bind('<<ListboxSelect>>',LboxSelect)

#Chassis Number Text Box
chsTextBox=Text(root, height=1, width=18)
chsTextBox.place(x=newImgWidth,y=newImgHeight//2)
messInit='Image: '+str(gChassisNum)+'\n'
chsTextBox.insert(1.0,messInit)

#Section Number Text Box
outbox=Text(root, height=1, width=18)
outbox.place(x=newImgWidth,y=newImgHeight//2+35)

#Label Text Box
labelOutBox=Text(root, height=1, width=18)
labelOutBox.place(x=newImgWidth,y=newImgHeight//2+70)

#Message Text Box
messbox=Text(root, height=2,width=18)
messbox.place(x=newImgWidth,y=newImgHeight*3//4)
#messbox.place(x=newImgWidth//2,y=40)

#Define and Place Save button for text file or database based on Output Mode
#Database output not developed yet
if (gOutputMode==1):
    saveButton = tk.Button(text="Save to Database", activebackground="yellow", command = SavetoDB)
    saveButton.place(x=newImgWidth+15,y=newImgHeight//2-30)
else:
    saveButton = tk.Button(text="Save to Text File", activebackground="yellow", command = SavetoDB)
    saveButton.place(x=newImgWidth+15,y=newImgHeight//2-30)
    #closeFileButton = tk.Button(text="Close Text File", activebackground="yellow", command = CloseFile)
    #closeFileButton.place(x=newImgWidth+15,y=newImgHeight+13)    

#Define and Place Buttons
clearButton = tk.Button(text="Clear Data", activebackground="yellow", command = ClearTextBox)
clearButton.place(x=newImgWidth+15,y=newImgHeight-15)

nextFileButton = tk.Button(text="Next", activebackground="yellow", command = NextImg)
nextFileButton.place(x=newImgWidth+110,y=newImgHeight-45)

prevFileButton = tk.Button(text="Prev", activebackground="yellow", command = PrevImg)
prevFileButton.place(x=newImgWidth+110,y=newImgHeight-15)

#Close the output text file upon exiting application
atexit.register(CloseFile)

root.mainloop()