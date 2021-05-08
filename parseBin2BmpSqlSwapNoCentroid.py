#imports
import os
import numpy as np
import PIL
from PIL import Image, ImageDraw, ImageFont
import csv
import binascii
from numpy.lib.function_base import select
import pyodbc

# Function to connect to database
def connect():
    #setup database connection
    
    #server = 'DREW_OFFICE_PC'
    #server = 'DESKTOP-JR7TM63' 
    #database = 'ChassisScan2'
    username = 'pyUser' 
    password = 'pyPW' 
    print('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()
    #Test connection
    cursor.execute("SELECT @@version;") 
    row = cursor.fetchone() 
    while row: 
        print(row[0])
        row = cursor.fetchone()
    return cursor

# Function for converting horizontal scan data
def convertScanHorz(chassisNumArg, cursor):
    
    #This will turn off image generation for the R2 side
    gVert2 = 0

    cursor.execute('\
        SELECT LEFT(CONVERT(nvarchar(MAX), HorizontalData, 2),96) AS Horz\
        FROM ['+database+'].[dbo].['+table+']\
        WHERE [ChassisID] = ?\
        ORDER BY [ChassisID],[SectionID],[SliceID]\
        ', (chassisNumArg))
    
    dataBytes = ''
    numRows = 0
    
    #set height fixed for Horizontal image
    height = 384

    for row in cursor:
        horzData = row.Horz
        dataBytes += horzData
        numRows += 1

    output = ConvertToBytes(dataBytes)
    
    #Horizontal Scan
    scanType = 1

    #Create Image file(s)
    GenerateImage(height,numRows,chassisNumArg,output,scanType)

# Function for converting vertical R1 scan data
def convertScanVertR1(chassisNumArg,cursor):
    
    #This will turn off image generation for the R2 side
    gVert2 = 0

    #get scan data from database
    cursor.execute('\
    SELECT LEFT(CONVERT(nvarchar(MAX), VerticalData, 2),56) AS Vert1\
    FROM ['+database+'].[dbo].['+table+']\
    WHERE [ChassisID] = ?\
    ORDER BY [ChassisID],[SectionID],[SliceID]\
    ', (chassisNumArg))

    dataBytes = ''
    numRows = 0
    
    #set height fixed for Vertical image
    height = 224

    for row in cursor:
        vert1Data = row.Vert1
        dataBytes += vert1Data
        numRows += 1

    output = ConvertToBytes(dataBytes)
    
    #Vertical 1 Scan
    scanType = 2
    
    GenerateImage(height,numRows,chassisNumArg,output,scanType)

# Function for converting vertical R2 scan data
def convertScanVertR2(chassisNumArg,cursor):
    
    #This will drive image generation for the R2 side
    gVert2 = 1

    #get scan data from database
    cursor.execute('\
    SELECT RIGHT(CONVERT(nvarchar(MAX), VerticalData, 2),56) AS Vert1\
    FROM ['+database+'].[dbo].['+table+']\
    WHERE [ChassisID] = ?\
    ORDER BY [ChassisID],[SectionID],[SliceID]\
    ', (chassisNumArg))
    
    dataBytes = ''
    numRows = 0
    
    #set height fixed for Vertical image
    height = 224

    for row in cursor:
        vert1Data = row.Vert1
        dataBytes += vert1Data
        numRows += 1

    output = ConvertToBytes(dataBytes)

    #Vertical 2 Scan
    scanType = 3

    GenerateImage(height,numRows,chassisNumArg,output,scanType)

# No longer used - Function for converting both horizontal and vertical R1 scan data together
def convertScanHV(chassisNumArg,cursor):
    
    #This will turn off image generation for the R2 side
    gVert2 = 0
    
    #get vertical and horizontal scan data from database
    cursor.execute('\
    SELECT LEFT(CONVERT(nvarchar(MAX), VerticalData, 2),56) AS Vert1, LEFT(CONVERT(nvarchar(MAX), HorizontalData, 2),96) AS Horz\
    FROM ['+database+'].[dbo].['+table+']\
    WHERE [ChassisID] = ?\
    ORDER BY [ChassisID],[SectionID],[SliceID]\
    ', (chassisNumArg))

    dataBytes = ''
    numRows = 0
    
    #set height fixed for Vertical image
    height = 224 + 384

    for row in cursor:
        vert1Data = row.Vert1
        horzData = row.Horz
        dataBytes += vert1Data +horzData 
        numRows += 1

    output = ConvertToBytes(dataBytes)
    
    #Horizontal+Vertical 1 Scan
    scanType = 4
    
    GenerateImage(height,numRows,chassisNumArg,output,scanType)

# Function to convert Scan Data Bytes from database to Bit Array
def ConvertToBytes(dataBytes):
    #get length of input data
    dataBytesLen = len(dataBytes)
    inputLength = dataBytesLen

    #add some padding on the array for indexing
    dataBytesBuffer2 = ""
    dataBytes = "x" + dataBytes + "0"

    #Need to flip bits in each nibble
    #dictionary for swapping bit order within each nibble
    bitFlipDict =	{
        "x": "x",
        "0": "0",
        "1": "8",
        "2": "4",
        "3": "C",
        "4": "2",
        "5": "A",
        "6": "6",
        "7": "E",
        "8": "1",
        "9": "9",
        "A": "5",
        "B": "D",
        "C": "3",
        "D": "B",
        "E": "7",
        "F": "F"
    }

    #init string
    dataBytesFlipped = ""
    
    #flip bits within each nibble
    for char in dataBytes:
        replChar = bitFlipDict.get(char)
        dataBytesFlipped += replChar

    #Now need to flip all the nibbles in sections of 8
    #flip nibbles in 8 nibbles at a time
    for i in range(0,len(dataBytesFlipped)-8,8):
        dataBytesBuffer1 = dataBytesFlipped[i+8:i:-1]
        dataBytesBuffer2 += dataBytesBuffer1


    #convert string to a byte array
    ba = bytearray.fromhex(dataBytesBuffer2)   

    #create output bit array
    output = np.zeros((inputLength*4+24), dtype=int)
    byteScoot = 0
    endByteScoot = int(inputLength/2)

    #convert from bytes to bits
    for byteScoot in range(0,endByteScoot):
        x = 128
        for i in range(0,8):
            result = ba[byteScoot] & x
            if (result):
                output[(byteScoot*8)+i] = 0
            else:
                output[(byteScoot*8)+i] = 255
            x = x >> 1
    return output

# Function to generate the output image and save to disk
def GenerateImage(height,numRows,chassisNumArg,outputBitArray,scanType):

    if gImtype:
        sliceMult = 5
    else:
        sliceMult = 1

    #create image
    slices = numRows
    width = (slices*sliceMult)
    im = Image.new("L", (width,height),0)
    print(chassisNumArg)
    print(im.format, im.size, im.mode)
    pixelo = im.load()

    if gVert2:
        #populate image file bits
        for k in range (0,slices):
            scoot = k*height-46
            for j in range (sliceMult):
                for i in range(height):
                    pixelo[j+k*sliceMult,i] = (outputBitArray[i+scoot].item(),)
    else:
        #populate image file bits
        for k in range (0,slices):
            scoot = k*height
            for j in range (sliceMult):
                for i in range(height):
                    pixelo[j+k*sliceMult,height-1-i] = (outputBitArray[i+scoot].item(),)

    #add section lines
    if (printLines):
        for k in range(0,slices*sliceMult,14*sliceMult):
            scoot = k*height
            for i in range(height):
                pixelo[k,height-1-i] = 50
        #add text
        numSect = int(numRows/14)
        fnt = ImageFont.truetype(font="arial", size=14, index=0, encoding="")

        if gVert2:
            secttextY=17
            chstextY=30
        else:
            secttextY=height-17
            chstextY=height-30

        if (scanType==2):
            for i in range(0,numSect):
                d = ImageDraw.Draw(im)
                outString = "Sec " + str(i+1)
                d.text((i*70+10,secttextY), outString, fill=(0), font=fnt)

            d = ImageDraw.Draw(im)
            outString = "Chassis " + chassisNumArg
            d.text((10,chstextY), outString, fill=(0), font=fnt)

    if(scanType==1):
        fileName = imagePath + chassisNumArg + "H." + outputImageType
    elif(scanType==2):
        fileName = imagePath + chassisNumArg + "V1." + outputImageType
    elif(scanType==3):
        fileName = imagePath + chassisNumArg + "V2." + outputImageType
    elif(scanType==4):
        fileName = imagePath + chassisNumArg + "HV1." + outputImageType

    #save output image file
    im.save(fileName)

def FlipVert2(chassisNumArg):
    im=Image.open(imagePath+chassisNumArg+'V2.' + outputImageType)
    out = im.transpose(PIL.Image.FLIP_TOP_BOTTOM)
    out.save(imagePath+chassisNumArg+'V2F.' + outputImageType)

def ConcatImages(chassisNumArg):
    imH=Image.open(imagePath+chassisNumArg+'H.' + outputImageType)
    imV1=Image.open(imagePath+chassisNumArg+'V1.' + outputImageType)
    imV2=Image.open(imagePath+chassisNumArg+'V2.' + outputImageType)
    outImage = Image.new("L",(imH.width,imH.height+imV1.height+imV2.height))
    outImage.paste(imV2,(0,0))
    outImage.paste(imH,(0,imV2.height))
    outImage.paste(imV1,(0,imV2.height+imH.height))
    outImage.save(concatImagePath+chassisNum+'.'+outputImageType)

#----- Main -----************************************
# set desired image type to be passed in as parameter
# 0 = raw
# 1 = stretched
gImtype = 1

# whether to flip the Robot 2 image
gVert2 = 0

# determines whether the output image has section lines, numbers and chassis number
printLines = False

#output image type driven by file extension - ex: bmp, jpg
outputImageType = 'bmp'

#assign database variables and output paths
server = 'DREW_OFFICE_PC'
database = 'ChassisScan2'
table = 'tbl_Robot_PhotoEyeLog'
imagePath = "C:/TestFiles5/outputimagesA/"
if not os.path.exists(imagePath):
    os.makedirs(imagePath)
concatImagePath = "C:/TestFiles5/concatImagesA/"
if not os.path.exists(concatImagePath):
    os.makedirs(concatImagePath)

#connect to database
gCurs = connect()

#Set starting and ending Chassis numbers
startChassis = 377801
endChassis = 377900

#start processing
for i in range(startChassis,endChassis):
    chassisNum = str(i)
    convertScanHorz(chassisNum,gCurs)

for i in range(startChassis,endChassis):
    chassisNum = str(i)
    convertScanVertR1(chassisNum,gCurs)  

for i in range(startChassis,endChassis):
    chassisNum = str(i)
    convertScanVertR2(chassisNum,gCurs)

for i in range(startChassis,endChassis):
    chassisNum = str(i)
    #FlipVert2(chassisNum)
    ConcatImages(chassisNum)
