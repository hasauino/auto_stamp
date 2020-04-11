import cv2
import numpy as np
import sys
from pdf2image import convert_from_path
from os import listdir
from PIL import Image, ImageTk
from os import mkdir, path


class StampBot:
    def __init__(self):
        self.stamp_ratio = 0.2
        self.step_ratio = 0.1
        self.docs_dir = None
        self.stamp_path = None
        self.stamp = None
        self.ready = False
        self.print = None

    @staticmethod
    def add_stamp(doc, stamp, stamp_ratio=0.2, step_ratio=0.1):
        doc_rows, doc_col, _ = doc.shape
        stamp_rows, stamp_cols, _ = stamp.shape
        k = stamp_rows/stamp_cols
        r = np.sqrt((doc_rows)**2 + (doc_col)**2)*stamp_ratio
        new_col = np.sqrt(r**2 / (k**2 + 1))
        new_row = k*new_col
        new_size = (int(new_col), int(new_row))
        stamp = cv2.resize(stamp, new_size, cv2.INTER_AREA)
        stamp_rows, stamp_cols, _ = stamp.shape
        gray = cv2.cvtColor(stamp, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY_INV)
        graydoc = cv2.cvtColor(doc, cv2.COLOR_BGR2GRAY)
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

    def stamp_all(self):
        try:
            files = listdir(self.docs_dir)
        except FileNotFoundError as e:
            self.print(e)
            sys.exit()

        out_dir = self.docs_dir+"/out_docs"
        if not path.exists(out_dir):
            mkdir(out_dir)

        if not path.exists(self.stamp_path):
            self.print("Couldn't find stamp image (stamp.png)")
            sys.exit()

        stamp = cv2.imread(self.stamp_path)

        for i, file in enumerate(files):
            if file[-3:].lower() != "pdf":
                continue
            pages = convert_from_path(self.docs_dir+'/'+file, dpi=400)
            stamped_pages = []
            for page in pages:
                doc = np.array(page)
                doc = cv2.cvtColor(doc, cv2.COLOR_BGR2RGB)
                doc = self.add_stamp(doc, stamp, stamp_ratio=self.stamp_ratio)
                doc = cv2.cvtColor(doc, cv2.COLOR_RGB2BGR)
                page = Image.fromarray(doc)
                stamped_pages.append(page)
            stamped_pages[0].save(out_dir+"/"+file[:-4]+".pdf", save_all=True,
                                  append_images=stamped_pages[1:])
            self.print("stammped file: ",
                  i+1, " progress: ",
                  (i+1.0)/len(files)*100.0, "%")
        self.print("done")

    def preview(self):
        try:
            files = listdir(self.docs_dir)
        except FileNotFoundError as e:
            self.print(e)
            sys.exit()
        if not path.exists(self.stamp_path):
            self.print("Couldn't find stamp image (stamp.png)")
            sys.exit()
        stamp = cv2.imread(self.stamp_path)
        for i, file in enumerate(files):
            if file[-3:].lower() != "pdf":
                continue
            page = convert_from_path(self.docs_dir+'/'+file, dpi=400)[0]
            doc = np.array(page)
            doc = cv2.cvtColor(doc, cv2.COLOR_BGR2RGB)
            ratio = doc.shape[1]/doc.shape[0]
            doc = self.add_stamp(doc, stamp, stamp_ratio=self.stamp_ratio)
            doc = cv2.cvtColor(doc, cv2.COLOR_RGB2BGR)
            page = Image.fromarray(doc)
            size = 600
            page = page.resize((int(size*ratio), size))
            return ImageTk.PhotoImage(page)
