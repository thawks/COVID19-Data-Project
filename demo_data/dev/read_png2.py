import cv2
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import pytesseract
import argparse
import os

# flags = [i for i in dir(cv) if i.startswith("COLOR_")]
#
# table = cv.imread("image_files/ohio_all_cases.png")
# gray_table = cv.cvtColor(table, cv.COLOR_BGR2GRAY)
# corners = cv.goodFeaturesToTrack(gray_table,25,0.01,10)
# for i in corners:
#     x,y = i.ravel()
#     cv.circle(table, (x,y), 3, 255, -1)
#
# plt.imshow(table), plt.show()
#rgb = cv.cvtColor(table, cv.COLOR_BGR2RGB)
#text = pytesseract.image_to_data(rgb, output_type=pytesseract.Output.DATAFRAME)

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
                help="path to input image")
ap.add_argument("-p", "--preprocess", type=str, default="thresh",
                help="type of preprocessing")
args = vars(ap.parse_args())
image = cv2.imread(args["image"])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

if args["preprocessing"] == "thresh":
    gray = cv2.threshold(gray, 0 , 255,
         cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

elif args["preprocessing"] == "blur":
    gray = cv2.medianBlur(gray, 3)

filename = "{}.png".format(os.getpid())
cv2.imwrite(filename, gray)

text = pytesseract.image_to_string(Image.open(filename))
os.remove(filename)
print(text)

cv2.imshow("Image", image)
cv2.imshow("Output", gray)
cv2.waitKey(0)