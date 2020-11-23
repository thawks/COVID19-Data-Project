import cv2
import pytesseract
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# read image in from memory
image = cv2.imread("image_files/NCDHHS_Alexander_county.png")
# set locations to apply ocr (top, left, bottom, right)
ocr_locations = dict(cases=(0,0,1590,1398))
def first_try(image, ocr_locations):
    # identify valid words for extraction
    key_values = ["american", "indian", "alaskan", "native", "asian", "or", "pacific", "islander", "black", "or", "african",
                  "american", "white", "other", "hispanic", "non-", "hispanic", "suppressed"]
    # instantiate dict for parse results, loop over ocr_locations to extract ocr'd contents, parse into
    # either cats (category) or counts.
    cats = []
    counts = []
    for cat, loc in ocr_locations.items():
        (t, l, b, r) = loc
        roi = image[t:b, l:r]
        rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        text = pytesseract.image_to_string(rgb)
        temp_cat = []
        # parse ocr'd text to format data
        for line in text.split("\n"):
            if len(line.strip()) == 0:
                continue
            for word in line.split():
                if word.lower() in key_values:
                    temp_cat.append(word)
                elif word.startswith("(") and word.endswith(")"):
                    word = int(word.strip("()").replace(",", ""))
                    counts.append(word)
                    cats.append("".join(temp_cat))
                    temp_cat = []
    return text, pd.DataFrame({"categories": cats, "counts": counts})


def try_two(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    dst = cv2.cornerHarris(gray, 20, 3,0.04)
    dst = cv2.dilate(dst, None)
    image[dst>.01*dst.max()] = [0,0,255]
    cv2.imshow('dst', image)
    k = cv2.waitKey(0)
    if k == ord("s"):
        cv2.destroyAllWindows()

def try_three():
    flags = [i for i in dir(cv2) if i.startswith('COLOR_')]
