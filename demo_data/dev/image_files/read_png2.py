import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

flags = [i for i in dir(cv) if i.startswith("COLOR_")]

table = cv.imread("NCDHHS_Alexander_county.png")
gray = cv.cvtColor(table, cv.COLOR_BGR2GRAY)
gray = np.float32(gray)
dst = cv.cornerHarris(gray, 20, 31,0.04)
dst = cv.dilate(dst, None)
table[dst>.01*dst.max()] = [0,0,255]
plt.imshow(table)
plt.show()