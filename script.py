#the code is written for Coursera's Python 3 Programming Specialisation's last Python Project: pillow, pytesseract and opencv
#actually coded for Jupyter Notebook IPython 

from zipfile import ZipFile

from PIL import Image, ImageDraw
import pytesseract
import cv2 as cv
import numpy as np

# loading the face detection classifier
face_cascade = cv.CascadeClassifier('readonly/haarcascade_frontalface_default.xml')

#extract images from zipfile

images_listarr=[]
images_binarized=[]
image_path=[]

file_name = "small_img.zip"

images_listarr=[]
images_list=[]
images_binarized=[]
image_path=[]

file_name = "small_img.zip"

def extract_images():
    with ZipFile("readonly/"+file_name, 'r') as zip:
        for info in zip.infolist():
            img_bytes = zip.open(info)
            pil_img = Image.open(img_bytes)  #pillow image
            image_arr = np.array(pil_img, np.uint8)   #image as ndarray
            if not(info.filename in image_path):
                image_bin = cv.threshold(cv.cvtColor(image_arr, cv.COLOR_BGR2GRAY), 180, 255, cv.THRESH_BINARY)[1]
                images_listarr.append(image_arr)
                images_list.append(pil_img)
                images_binarized.append(image_bin)
                image_path.append(info.filename)

def identify_text_regions(image):   #image is a binarized ndarray
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (1,1)) 
    #now dilate
    image = cv.resize(image, None, fx=5, fy=5, interpolation=cv.INTER_LINEAR)
    dilation = cv.dilate(image.copy(), kernel)  
    #now find contours
    _, contours,heirarchy = cv.findContours(dilation, mode= cv.RETR_EXTERNAL, method=cv.CHAIN_APPROX_NONE)  
    
    #print(contours, len(contours))
    display(contours)
    for contour in contours[0]:
        rect = cv.boundingRect(contour)
        if rect[2] < 50 or rect[3] < 50 : 
            continue
        print (cv.contourArea(contour))
        print(rect)
        x,y,w,h = rect
        #print(x,y,w,h)
        #crop image and send to OCR
        #but first, I will draw rectangles around the textcolumns
        cv.rectangle(image, (x,y), (x+w,y+h), (0,255,0), 2)
        #obj = ImageDraw.Draw(images_list[1])
        #obj.rectangle((x,y,x+w, y+h), fill=None, outline="red")
        
    
    display(Image.fromarray(image))


def extract_text(path):
    lookup=[]
    entry=[]
    for i in range(0, len(image_path)):
        entry=[]
        entry.append(image_path[i]) #take care of the filename
        text = list(pytesseract.image_to_string(images_list[i]).replace('\n',' ').split(" ")) 
        entry.append(text)
        lookup.append(entry)
    return lookup

        
def detect_faces(image, index): 
    
    x=0
    y=0
    faces = face_cascade.detectMultiScale(image, 1.35)
    contact_sheet=Image.new(images_list[0].mode, (90*5,90*(1+len(faces)//5)))
    
    if(len(faces)==0):
        print("No faces detected in the file")
        return
    
    #obj = ImageDraw.Draw(images_list[0])  #PIL images
    
    for face in faces:
        img= images_list[index].crop((face[0],face[1], face[0]+face[2], face[1]+face[3]))
        if img.width>90 or img.height>90:
            img.thumbnail((90,90))
        contact_sheet.paste(img, (x, y))
        if x+img.width >= contact_sheet.width:
            x=0
            y=y+img.height
        else:
            x=x+img.width
    
    display(contact_sheet)


def lookup_keyword(all_text, keyword):
    for i in range(0, len(all_text)):
        filename = all_text[i][0]
        print(filename)
        text = all_text[i][1]
        print(text)
        if keyword in text:
            #pass the image to face detector
            print("Results found in file "+filename)
            detect_faces(images_listarr[i],i)
            

all_text=[]
def lookup():
    global all_text
    print("Enter the search keyword")
    keyword = input()    
    #OCR
    all_text = extract_text(file_name)
    #now, look for the word in the images via tesseract
    lookup_keyword(all_text, keyword)

    #first, detect all text- regions using opencv    (??? not required)


lookup()
