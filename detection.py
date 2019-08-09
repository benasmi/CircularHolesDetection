from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog,ttk
import PyDIP as dip
import numpy as np
import cv2
import imutils
import math

benchmark_filename = ""
part_filename = ""

benchmark_img = None
part_img = None
part_img_rgb = None
part_calibrated_img = None

height=1050
width=1600

benchmark_circles_list = []
part_circles_list = []

image_width = width/4
results_width = width/1.3


def getThreeChannelPhoto(img):
    img2 = np.zeros_like(img)
    img2[:,:,0] = img
    img2[:,:,1] = img
    img2[:,:,2] = img
    return img2

def getArrowCoordinates(dx, dy, x, y, length):
    tan = dx / dy
    sine = np.sqrt(tan ** 2 / (1 + tan ** 2))
    cosine = np.sqrt(1 / (1 + tan ** 2))
    return [(int(x), int(y)), (int(cosine * length + x), int(sine * length + y))]


def getMiddlePoint(p1, p2):
    return [int((p1[0] + p2[0]) / 2), int((p1[1] + p2[1]) / 2)]


def sumCoordinates(p1, p2):
    return (int(p1[0] + p2[0]), int(p1[1] + p2[1]))


def getHypotenuse(p):
    return np.sqrt(p[0] ** 2 + p[1] ** 2)


def displayResults(targetImg, benchmark_circles, part_circles):
    targetImg = cv2.cvtColor(targetImg, cv2.COLOR_GRAY2RGB)
    for c1, c2 in zip(benchmark_circles, part_circles):
        dx = c1[0] - c2[0]
        dy = c1[1] - c2[1]
        arrowCoordinates = getArrowCoordinates(dx, dy, c1[0], c1[1], 400)
        midpoint = getMiddlePoint(arrowCoordinates[0], arrowCoordinates[1])
        midpoint = (
            midpoint[0], midpoint[1] + 50)  # We want the text to be above the line, so we increment the y coordinate
        offset = round(getHypotenuse((dx, dy)), 2)

        if abs(c1[2] - c2[2]) > 5:
            circle_color = (255, 0, 0)
        else:
            circle_color = (0, 255, 0)
        if abs(offset) > 5:
            arrow_color = (255, 0, 0)
        else:
            arrow_color = (0, 255, 0)

        cv2.arrowedLine(targetImg, arrowCoordinates[0], arrowCoordinates[1], arrow_color, 10)
        cv2.putText(targetImg, "dL={}".format(offset), (int(c1[0] - 50), int(c1[1] + 80)), cv2.FONT_HERSHEY_SIMPLEX, 3,
                    (156, 188, 24), 3)
        cv2.putText(targetImg, "dR={}".format(round(c1[2] / 2 - c2[2] / 2, 3)), (int(c1[0] - 50), int(c1[1])),
                    cv2.FONT_HERSHEY_SIMPLEX, 3, (156, 188, 24), 3)
        cv2.circle(targetImg, (int(c2[0]), int(c2[1])), int(c1[2] / 2), circle_color, 5)
    return targetImg

def distanceToCircle(circle1, circle2):
    return math.sqrt(((circle1[0] - circle2[0]) ** 2) + ((circle1[1] - circle2[1]) ** 2))

def unitedCircleData(circle1, circle2):
    global benchmark_circles_list,part_circles_list
    min_distance = distanceToCircle(circle1[0], circle2[0])
    benchmark_circle = circle1[0]
    part_circle = circle2[0]

    for c1 in circle1:
        for c2 in circle2:
            distance = distanceToCircle(c1,c2)
            if(distance<min_distance):
                min_distance=distance
                benchmark_circle = c1
                part_circle = c2


    benchmark_circles_list.append(benchmark_circle)
    part_circles_list.append(part_circle)
    circle1.remove(benchmark_circle)
    circle2.remove(part_circle)
    if(len(circle1)==0 or len(circle2)==0):
        print("Valio!!!")
    else:
        unitedCircleData(circle1,circle2)


def calculateDiameters(img):
    list_circle_data = []
    index = 0
    bin, thresh = dip.Threshold(img)
    bin = dip.EdgeObjectsRemove(bin)
    bin = dip.Label(bin)

    bin = dip.Dilation(bin, 10) # we need larger regions to average over so we take all of the light coming through the hole into account.
    img = (dip.ErfClip(img, thresh, thresh/4, "range") - (thresh*7/8)) / (thresh/4)
    msr = dip.MeasurementTool.Measure(bin, img, features=['Mass', 'Center'])
    d3 = np.sqrt(np.array(msr['Mass'])[:,0] * 4 / np.pi)
    print("method 3:", d3)
    for center, diameter in zip(np.array(msr['Center']), d3):
        list_circle_data.append((center[0], center[1], diameter, index))
        index = index + 1
        print(str(center))
    return list_circle_data

def resizedImage(width, image):
    img = imutils.resize(image, width=int(width))
    return ImageTk.PhotoImage(Image.fromarray(np.array(img)))

def openFileDialog():
    filename = filedialog.askopenfilename(initialdir="/", title="Select file",filetypes=(("jpeg files", "*.bmp"), ("all files", "*.*")))
    return filename

def select_benchmark_photo():
    global benchmark_filename, benchmark_img
    benchmark_filename = openFileDialog()
    benchmark_img = cv2.imread(benchmark_filename, 0)
    temp_img = resizedImage(image_width,benchmark_img)
    benchmark_panel.configure(image=temp_img)
    benchmark_panel.image = temp_img
    labelBenchmark.config(text=benchmark_filename)

def select_part_photo():
    global part_filename, part_img, part_img_rgb
    part_filename = openFileDialog()
    part_img = cv2.imread(part_filename, 0)
    part_img_rgb = cv2.imread(part_filename,1)
    temp_img = resizedImage(image_width,part_img)
    part_panel.configure(image=temp_img)
    part_panel.image = temp_img
    labelPart.config(text=part_filename)


def calculate():
    global part_calibrated_img
    #Finding transformations...
    print("Calibrating...")
    part_calibrated_img = calibratePosition(benchmark_img, part_img)


    #Measuring diameters...
    benchmark_circle = calculateDiameters(benchmark_img)
    labelProgress.config(text="Measuring new part diameters...")
    part_circle = calculateDiameters(part_calibrated_img)

    #Calculating differences...
    labelProgress.config(text="Calculating differences...")
    unitedCircleData(benchmark_circle,part_circle)

    #Displaying erros...
    print("Etalons")
    print(benchmark_circles_list)
    print("Kita detale")
    print(part_circles_list)

    results_img = displayResults(part_calibrated_img, benchmark_circles_list, part_circles_list)
    cv2.imwrite("Results.bmp", results_img)

    temp_img = resizedImage(results_width, results_img)

    results_panel.configure(image=temp_img)
    results_panel.image = temp_img


    #for c in benchmark_circles_list:
    #    cv2.putText(im1, "{}".format(benchmark_circles_list.index(c)), (int(c[0]) - 50, int(c[1]) - 50), cv2.FONT_HERSHEY_SIMPLEX, 3,(156, 188, 24), 3)
    #cv2.imwrite("A1_pasposyts.bmp", im1)

def calibratePosition(im1, im2):


    # Convert images to grayscale
    #im1_gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
    #im2_gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

    # Find size of image1
    sz = im1.shape

    # Define the motion model
    warp_mode = cv2.MOTION_EUCLIDEAN

    # Define 2x3 or 3x3 matrices and initialize the matrix to identity
    if warp_mode == cv2.MOTION_HOMOGRAPHY:
        warp_matrix = np.eye(3, 3, dtype=np.float32)
    else:
        warp_matrix = np.eye(2, 3, dtype=np.float32)

    # Specify the number of iterations.
    number_of_iterations = 5000;

    # Specify the threshold of the increment
    # in the correlation coefficient between two iterations
    termination_eps = 1e-10;

    # Define termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations, termination_eps)

    print("Finding transformations...")
    # Run the ECC algorithm. The results are stored in warp_matrix.
    (cc, warp_matrix) = cv2.findTransformECC(im1, im2, warp_matrix, warp_mode, criteria, None, 1)
    print("Transformations found!")
    if warp_mode == cv2.MOTION_HOMOGRAPHY:
        # Use warpPerspective for Homography
        im2_aligned = cv2.warpPerspective(im2, warp_matrix, (sz[1], sz[0]),
                                          flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
    else:
        # Use warpAffine for Translation, Euclidean and Affine
        im2_aligned = cv2.warpAffine(im2, warp_matrix, (sz[1], sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP);
    return im2_aligned



root = Tk()


root.resizable(width=FALSE,height=FALSE)
root.geometry('1680x1050')


#Left frame
left_frame = Frame(root, width=width/1.3, height=height)
left_frame.pack_propagate(False)
#Right frame
right_frame = Frame(root, width=width/1.3, height=height)
right_frame.pack_propagate(False)

left_frame.grid(row=0,column=0, sticky="NWS", padx=(20,0))
right_frame.grid(row=0,column=1, sticky="NES", padx=(20,0))

#########
#Left top
left_top = Frame(left_frame, width=width/1.3, height=height/2)
left_top.pack(side=TOP, anchor=NW)
left_top.pack_propagate(False)

btnBenchmark = Button(left_top, text="Pasirinkti etaloną", command=select_benchmark_photo,highlightthickness=0)
btnPart = Button(left_top, text="Pasirinkti detalę", command=select_part_photo)
btnCalculate = Button(left_top, text="Skaičiuoti", width=20, command=calculate)
labelBenchmark = Label(left_top, text="Nepasirinkta")
labelPart = Label(left_top, text="Nepasirinkta")
labelResults = Label(left_top)
labelResults.config(text="1. Pasirenkame etaloninę nuotrauką\n"
                         "2. Pasirenkame tikrinamamos detalės nuotrauką\n"
                         "3. Raudona spalva poslinkio/diametro paklaida >=5px\n"
                         "4. Žalia spalva poslinkio/diametro paklaida <=5px\n")
labelProgress = Label(left_top, text="")

btnBenchmark.grid(row=0,column=0)
btnPart.grid(row=1,column=0)
btnCalculate.grid(row=2, columnspan=2)
labelBenchmark.grid(row=0,column=1)
labelPart.grid(row=1,column=1)
labelResults.grid(row=3, columnspan=10)
labelProgress.grid(row=4, column=0)



#Left Bottom
left_bottom = LabelFrame(left_frame, width=width/1.3, height=height/1.3, text="REZULTATAI")
left_bottom.pack(side=BOTTOM)
left_bottom.pack_propagate(False)

results_panel = Label(left_bottom, width=int(width/1.3), height=int(height/1.3))
results_panel.pack(side=TOP, anchor=N)
##########



##########
#Right top
right_top = LabelFrame(right_frame, width=width/4, height=height/2, text="ETALONAS")
right_top.pack_propagate(False)

#Right bottom
right_bottom = LabelFrame(right_frame, width=width/4, height=height/2, text="NAUJA DETALĖ")
right_bottom.pack_propagate(False)

right_top.grid(row=0,column=0)
right_bottom.grid(row=1,column=0)

benchmark_panel = Label(right_top, width=int(width/4), height=int(height/2))
benchmark_panel.pack(side=TOP, anchor=N)

part_panel = Label(right_bottom, width=int(width/4), height=int(height/2))
part_panel.pack(side=BOTTOM)
##########

root.mainloop()


