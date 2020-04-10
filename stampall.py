#!/usr/bin/python3
import cv2
import numpy as np
import sys
from pdf2image import convert_from_path
from os import listdir
from PIL import Image
from os import mkdir
def add_stamp(doc, stamp, stamp_ratio=0.2, step_ratio=0.1):
    doc_rows, doc_col, _ = doc.shape
    stamp_rows, stamp_cols, _ = stamp.shape
    k = stamp_rows/stamp_cols
    r = np.sqrt((doc_rows)**2 + (doc_col)**2)*stamp_ratio
    new_col = np.sqrt(r**2 / (k**2 + 1))
    new_row = k*new_col
    new_size = (int(new_row), int(new_col))
    stamp = cv2.resize(stamp, new_size, cv2.INTER_AREA)
    stamp_rows, stamp_cols, _ = stamp.shape
    gray = cv2.cvtColor(stamp, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 245,255,cv2.THRESH_BINARY_INV)


    graydoc = cv2.cvtColor(doc, cv2.COLOR_BGR2GRAY)
    n_col = int(np.ceil(doc_col*0.5/stamp_cols))
    n_row = int(doc_rows*0.5/stamp_rows)
    step_check = int(step_ratio*doc_col)
    centers = []
    white_values = []
    center = [doc_rows, doc_col]
    while (center[1] > int(doc_col*0.5)):
        while (center[0] > int(doc_rows*0.5)):
            centers.append(np.copy(center))
            white_values.append(graydoc[center[0]-stamp_rows:center[0],
                                        center[1]-stamp_rows:center[1]].mean())
            center[0] -= step_check
        center[1] -= step_check
        center[0] = doc_rows
    centers = centers[::-1]
    white_values = white_values[::-1]
    location = centers[np.argmax(white_values)]
    pos_x = location[0] - stamp_rows
    pos_y = location[1] - stamp_cols
    roi = doc[pos_x:pos_x+stamp_rows, pos_y:pos_y+stamp_cols]
    mask_inv = cv2.bitwise_not(mask)
    anded = cv2.bitwise_and(roi, roi, mask=mask_inv)
    stamp = cv2.bitwise_and(stamp, stamp, mask=mask)
    dst = cv2.add(anded, stamp)
    doc[pos_x:pos_x+stamp_rows, pos_y:pos_y+stamp_cols] = dst
    return doc


try:
    files = listdir("docs")
except FileNotFoundError as e:
    print(e)
    exit()

mkdir('out_docs')

stamp = cv2.imread('stamp.png')


for i, file in enumerate(files):
    pages = convert_from_path('docs/'+file, dpi=400)
    stamped_pages = []
    for page in pages:
        doc = np.array(page)
        doc = cv2.cvtColor(doc, cv2.COLOR_BGR2RGB)
        doc = add_stamp(doc, stamp)
        doc = cv2.cvtColor(doc, cv2.COLOR_RGB2BGR)
        page = Image.fromarray(doc)
        stamped_pages.append(page)
    stamped_pages[0].save("out_docs/"+file[:-4]+".pdf", save_all=True, 
                          append_images=stamped_pages[1:])
    print("stammped file:   ", i+1, "  progress: ", (i+1.0)/len(files)*100.0, "%")
