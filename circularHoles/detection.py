from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog
import PyDIP as dip
import numpy as np

benchmark_filename = ""
part_filename = ""

def calculateDiameters(fileName):
    img = dip.ImageRead(fileName)
    img.SetPixelSize(dip.PixelSize(dip.PhysicalQuantity(1,'um'))) # Usually this info is in the image file
    bin, thresh = dip.Threshold(img)
    bin = dip.EdgeObjectsRemove(bin)
    bin = dip.Label(bin)

    bin = dip.Dilation(bin, 10) # we need larger regions to average over so we take all of the light coming through the hole into account.
    img = (dip.ErfClip(img, thresh, thresh/4, "range") - (thresh*7/8)) / (thresh/4)
    msr = dip.MeasurementTool.Measure(bin, img, features=['Mass'])
    d3 = np.sqrt(np.array(msr['Mass'])[:,0] * 4 / np.pi)
    print("method 3:", d3)
    return d3


def resizedImage(desiredWidth, path):
    image = Image.open(path)
    image_height = int((desiredWidth / image.size[0]) * image.size[1])
    image = image.resize((int(image_width), int(image_height)), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(image)
    return img

def openFileDialog():
    filename = filedialog.askopenfilename(initialdir="/", title="Select file",filetypes=(("jpeg files", "*.bmp"), ("all files", "*.*")))
    return filename

def select_benchmark_photo():
    global benchmark_filename
    benchmark_filename = openFileDialog()
    img = resizedImage(image_width, benchmark_filename)
    benchmark_panel.configure(image=img)
    benchmark_panel.image = img
    labelBenchmark.config(text=benchmark_filename)

def select_part_photo():
    global part_filename
    part_filename = openFileDialog()
    img = resizedImage(image_width, part_filename)
    part_panel.configure(image=img)
    part_panel.image = img
    labelPart.config(text=part_filename)

def calculate():
    diameters = calculateDiameters(benchmark_filename)
    labelResults.config(text=diameters)



height=1050
width=1680

image_width = width/2.5

root = Tk()
root.resizable(width=FALSE,height=FALSE)
root.geometry('1680x1050')




#########################################################################################
#Left frame
left_frame = Frame(root, width=width/2, height=height)
left_frame.pack(side=LEFT)
left_frame.pack_propagate(False)

#*********************************#
#Left top
left_top = Frame(left_frame, width=width/2, height=height/2)
left_top.pack(side=TOP, anchor=NW)
left_top.pack_propagate(False)

btnBenchmark = Button(left_top, text="Pasirinkti etaloną", command=select_benchmark_photo)
btnPart = Button(left_top, text="Pasirinkti detalę", command=select_part_photo)
btnCalculate = Button(left_top, text="Skaičiuoti", width=20, command=calculate)
labelBenchmark = Label(left_top, text="Nepasirinkta")
labelPart = Label(left_top, text="Nepasirinkta")
labelResults = Label(left_top)

btnBenchmark.grid(row=0,column=0)
btnPart.grid(row=1,column=0)
btnCalculate.grid(row=2, columnspan=2)
labelBenchmark.grid(row=0,column=1)
labelPart.grid(row=1,column=1)
labelResults.grid(row=3, columnspan=10)


#Left Bottom
left_bottom = Frame(left_frame, width=width/2, height=height/2,bg="pink")
left_bottom.pack(side=BOTTOM)
left_bottom.pack_propagate(False)
#*********************************#

#########################################################################################




#########################################################################################
#Right frame
right_frame = Frame(root, width=width/2, height=height)
right_frame.pack(side=RIGHT)
right_frame.pack_propagate(False)

#*********************************#
#Right top
right_top = Frame(right_frame, width=width/2, height=height/2, bg="black", bd=1)
right_top.pack(side=TOP, anchor=N)
right_top.pack_propagate(False)

benchmark_panel = Label(right_top, width=int(width/2), height=int(height/2))
benchmark_panel.pack(side=TOP, anchor=N)

#Right bottom
right_bottom = Frame(right_frame, width=width/2, height=height/2,bg="black", bd=1)
right_bottom.pack(side=BOTTOM)
right_bottom.pack_propagate(False)

part_panel = Label(right_bottom, width=int(width/2), height=int(height/2))
part_panel.pack(side=BOTTOM)
#*********************************#


#########################################################################################


root.mainloop()
