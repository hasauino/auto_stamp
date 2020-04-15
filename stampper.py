import cv2
import numpy as np
import sys
from pdf2image import convert_from_path
from os import listdir
from PIL import Image, ImageTk
from os import mkdir, path
import re
from msgs import error_msgs as err
from random import randint
from msgs import log_msgs as log


class StampBot:
    def __init__(self):
        self.stamp_ratio = 0.2
        self.step_ratio = 0.1
        self.preview_size = 600
        self.docs_dir = None
        self.stamp_path = None
        self.stamp = None
        self.ready = False
        self.print = None
        pdf_re = r'.*\.pdf'
        img_re = r'.*\.(bmp|dib|jpeg|jpg|jpe|jp2|png|webp|pbm|pgm|ppm|pxm|pnm|pfm|sr|ras|tiff|tif|exr|hdr|pic)'
        self.pdf_pattern = re.compile(pdf_re, re.I)
        self.img_pattern = re.compile(img_re, re.I)
        self.file_pattern = re.compile("(%s|%s)" % (pdf_re, img_re))

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
        files, stamp = self._check_directory()
        if stamp is None:
            return None

        out_dir = self.docs_dir+"/out_docs"
        if not path.exists(out_dir):
            try:
                mkdir(out_dir)
            except:
                self.print(err.MKDIR_FAIL)
                return None
        failed_files = []
        for i, file in enumerate(files):
            if self.pdf_pattern.match(file):
                try:
                    pages = convert_from_path(self.docs_dir+'/'+file, dpi=400)
                except Image.DecompressionBombError:
                    pages = convert_from_path(self.docs_dir+'/'+file)
                except:
                    self.print(err.FILE_READ_FAIL, file)
                    failed_files.append(file)
                    continue
                stamped_pages = []
                for page in pages:
                    doc = np.array(page)
                    doc = cv2.cvtColor(doc, cv2.COLOR_BGR2RGB)
                    doc = self.add_stamp(doc, stamp,
                                         stamp_ratio=self.stamp_ratio)
                    doc = cv2.cvtColor(doc, cv2.COLOR_RGB2BGR)
                    page = Image.fromarray(doc)
                    stamped_pages.append(page)
                stamped_pages[0].save(out_dir+"/"+file[:-4]+".pdf",
                                      save_all=True,
                                      append_images=stamped_pages[1:])
            else:
                doc = cv2.imread(self.docs_dir+'/'+file)
                if doc is None:
                    self.print(err.FILE_READ_FAIL, file)
                    failed_files.append(file)
                    continue
                doc = self.add_stamp(doc, stamp, stamp_ratio=self.stamp_ratio)
                cv2.imwrite(out_dir+"/"+file, doc)

            self.print("stammped file: ",
                       i+1, " progress: ",
                       (i+1.0)/len(files)*100.0, "%")
        self.print(log.DONE_RUN)
        self.print(log.SUCCESS_FILES %
                   (len(files)-len(failed_files), len(files)))

    def preview(self, panel):
        files, stamp = self._check_directory()
        if stamp is None:
            return None
        rand_index = randint(0, len(files)-1)
        file = files[rand_index]
        if self.pdf_pattern.match(file):
            try:
                page = convert_from_path(self.docs_dir+'/'+file, dpi=400)[0]
            except Image.DecompressionBombError:
                page = convert_from_path(self.docs_dir+'/'+file)[0]
            except:
                self.print(err.FILE_READ_FAIL, file)
                return None

            doc = np.array(page)
            doc = cv2.cvtColor(doc, cv2.COLOR_BGR2RGB)
        else:
            doc = cv2.imread(self.docs_dir+'/'+file)
            if doc is None:
                self.print(err.FILE_READ_FAIL, file)
                return None

        ratio = doc.shape[1]/doc.shape[0]
        doc = self.add_stamp(doc, stamp, stamp_ratio=self.stamp_ratio)
        doc = cv2.cvtColor(doc, cv2.COLOR_RGB2BGR)
        page = Image.fromarray(doc)
        size = self.preview_size
        page = page.resize((int(size*ratio), size))
        img = ImageTk.PhotoImage(page)
        if img:
            panel.configure(image=img)
            panel.image = img
            self.print(log.PREVIEW_DONE)
        else:
            self.print(err.PREVIEW_FAIL)

    def _check_directory(self):
        try:
            files = [file for file in listdir(self.docs_dir)
                     if self.file_pattern.match(file)]
        except FileNotFoundError as e:
            self.print(e)
            return None, None
        if len(files) == 0:
            self.print(err.NO_FILES)
            return None, None
        if not path.exists(self.stamp_path):
            self.print(err.STAMP_NOT_FOUND)
            return None, None
        stamp = cv2.imread(self.stamp_path)
        if stamp is None:
            self.print(err.STAMP_READ_FAIL)
            if not self.img_pattern.match(self.stamp_path):
                self.print(err.STAMP_UNSUPPORTED)
            return None, None
        return files, stamp
