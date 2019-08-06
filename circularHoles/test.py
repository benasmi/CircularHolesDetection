import PyDIP as dip
import numpy as np
import cv2 as cv
import easygui
from tkinter import *
from tkinter import filedialog


global root
global benchmarkFileName
global partFileName
#buttons
global benchmarkBtn
global partBtn

def calculate(img):

    img.SetPixelSize(dip.PixelSize(dip.PhysicalQuantity(1,'um'))) # Usually this info is in the image file
    bin, thresh = dip.Threshold(img)
    bin = dip.EdgeObjectsRemove(bin)
    bin = dip.Label(bin)

    bin = dip.Dilation(bin, 10) # we need larger regions to average over so we take all of the light coming through the hole into account.
    img = (dip.ErfClip(img, thresh, thresh/4, "range") - (thresh*7/8)) / (thresh/4)
    msr = dip.MeasurementTool.Measure(bin, img, features=['Mass'])
    d3 = np.sqrt(np.array(msr['Mass'])[:,0] * 4 / np.pi)
    print("method 3:", d3)

def initializeWindows():

    #Root window
    root = Tk()
    root.title = "Circular holes detection"
    root.resizable(width=FALSE, height=FALSE)
    root.geometry('1920x1080')

    #Button
    benchmarkBtn = Button(root, text="Pasirinkti etaloną", command=benchmarkCallback)
    benchmarkBtn.pack()

    partBtn = Button(root, text="Pasirinkti naują detalę", command=partCallback)
    partBtn.pack()


    root.mainloop()

def openFileDialog():
    filename = filedialog.askopenfilename(initialdir="/", title="Select file",filetypes=(("jpeg files", "*.bmp"), ("all files", "*.*")))
    return filename

def benchmarkCallback():
    benchmarkFileName = openFileDialog()

    benchmarkBtn = Button(text=benchmarkFileName, command=benchmarkCallback, bg="blue")
    benchmarkBtn.grid(row=2, column=2, sticky=W)
    benchmarkBtn.pack

    print(benchmarkFileName)

def partCallback():
    partFileName = openFileDialog()
    print(partFileName)

initializeWindows()



img = dip.ImageRead('B1.bmp')

