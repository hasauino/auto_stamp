#!/usr/bin/python3

import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory
from stampper import StampBot


def stamp_chooser_event():
    text = stamp_path_field.get()
    selected = askopenfilename()
    if not len(selected) == 0:
        stamp_path_field.delete(first=0, last=len(text))
        stamp_path_field.insert(0, selected)


def dir_chooser_event():
    text = dir_field.get()
    selected = askdirectory()
    if not len(selected) == 0:
        dir_field.delete(first=0, last=len(text))
        dir_field.insert(0, selected)


def run():
    bot.stamp_path = stamp_path_field.get()
    bot.docs_dir = dir_field.get()
    bot.stamp_all()


bot = StampBot()
root = tk.Tk()
root.geometry('400x600')
root.title("MENA auto stamp tool")


# stamp details
stamp_label = tk.Label(root, text="Choose stamp image:  ")
stamp_label.grid(column=0, row=0)
stamp_path_field = tk.Entry(root)
stamp_path_field.grid(column=0, row=1)
stamp_browse = tk.Button(root, text="Browse",
                         command=stamp_chooser_event)
stamp_browse.grid(column=1, row=1)

# docs directory
dir_label = tk.Label(root, text="Choose documents directory:  ")
dir_label.grid(column=0, row=2)
dir_field = tk.Entry(root)
dir_field.grid(column=0, row=3)

dir_browse = tk.Button(root, text="Browse",
                       command=dir_chooser_event)
dir_browse.grid(column=1, row=3)

# preview

# run
run_btn = tk.Button(root, text="Run",
                    command=run)
run_btn.grid(column=0, row=4)

root.mainloop()
