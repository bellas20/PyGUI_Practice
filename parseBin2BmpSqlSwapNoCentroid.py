#imports
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import csv
import binascii
import pyodbc

# Function to connect to database
def connect():
    #setup database connection
    server = 'DREW_OFFICE_PC' 
    database = 'ChassisScan2'
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
def convertScanHorzToBmp(chassisNumArg, cursor):
    
    cursor.execute('\
        SELECT LEFT(CONVERT(nvarchar(MAX), HorizontalData, 2),96) AS Horz\
        FROM [ChassisScan].[dbo].[tbl_Robot_PhotoEyeLog]\
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
  
    #Create Image file(s)
    GenerateImage(height,numRows,chassisNumArg,output)

# Function for converting vertical R1 scan data
def convertScanVert1ToBmp(chassisNumArg,cursor):
    
    #get scan data from database
    cursor.execute('\
    SELECT LEFT(CONVERT(nvarchar(MAX), VerticalData, 2),56) AS Vert1\
    FROM [ChassisScan].[dbo].[tbl_Robot_PhotoEyeLog]\
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

    GenerateImage(height,numRows,chassisNumArg,output)

# Function for converting both horizontal and vertical R1 scan data together
def convertScanHVToBmp(chassisNumArg,cursor):
    #get vertical and horizontal scan data from database
    cursor.execute('\
    SELECT LEFT(CONVERT(nvarchar(MAX), VerticalData, 2),56) AS Vert1, LEFT(CONVERT(nvarchar(MAX), HorizontalData, 2),96) AS Horz\
    FROM [ChassisScan2].[dbo].[tbl_Robot_PhotoEyeLog]\
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

    GenerateImage(height,numRows,chassisNumArg,output)

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
    output = np.zeros((inputLength*4), dtype=int)
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
def GenerateImage(height,numRows,chassisNumArg,outputBitArray):

    if gImtype:
        sliceMult = 5
    else:
        sliceMult = 1

    #create image
    slices = numRows
    width = (slices*sliceMult)
    im = Image.new("L", (width,height),0)
    print(im.format, im.size, im.mode)
    pixelo = im.load()

    #populate image file bits
    for k in range (0,slices):
        scoot = k*height
        for j in range (sliceMult):
            for i in range(height):
                pixelo[j+k*sliceMult,height-1-i] = (outputBitArray[i+scoot],)

    #add section lines
    for k in range(0,slices*sliceMult,14*sliceMult):
        scoot = k*height
        for i in range(height):
            pixelo[k,height-1-i] = 50

    if gImtype:
        #add text
        numSect = int(numRows/14)
        fnt = ImageFont.truetype(font="arial", size=14, index=0, encoding="")

        for i in range(0,numSect):
            d = ImageDraw.Draw(im)
            outString = "Sec " + str(i+1)
            d.text((i*70+10,height-17), outString, fill=(0), font=fnt)

        d = ImageDraw.Draw(im)
        outString = "Chassis " + chassisNumArg
        d.text((10,height-30), outString, fill=(0), font=fnt)

    if gImtype:
        fileName = "C:/TestFiles5/outputimages/" + chassisNumArg + "stretch.jpg"
    else:
        fileName = "C:/TestFiles5/outputimages/" + chassisNumArg + ".bmp"

    #save output image file
    im.save(fileName)


#----- Main -----************************************
# set desired image type to be passed in as parameter
# 0 = raw
# 1 = stretched
gImtype = 1

#connect to database
gCurs = connect()

#Set starting and ending Chassis numbers
startChassis = 377801
endChassis = 377850

#start processing
for i in range(startChassis,endChassis):
    chassisNum = str(i)
    convertScanHVToBmp(chassisNum,gCurs)



