#!/usr/bin/python3

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, askdirectory
from stampper import StampBot
import threading
from ttkthemes import ThemedTk


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
    bot.stamp_ratio = float(scale.get())
    bot.stamp_path = stamp_path_field.get()
    bot.docs_dir = dir_field.get()
    bot.print = _print
    t1 = threading.Thread(target=bot.stamp_all, args=[])
    t1.start()


def preview():
    bot.stamp_ratio = float(scale.get())
    bot.stamp_path = stamp_path_field.get()
    bot.docs_dir = dir_field.get()
    bot.print = _print
    img = bot.preview()
    panel.configure(image=img)
    panel.image = img


def _print(*argv):
    for arg in argv:
        text.insert(tk.INSERT, arg)
    text.insert(tk.INSERT, "\n")
    text.see("end")


bot = StampBot()
root = ThemedTk(theme="arc")
root.geometry('900x650')
root.title("MENA auto stamp tool")
root.configure(bg='#f5f6f7')

left = ttk.Frame(root)
left.grid(column=0, row=0)

right = ttk.Frame(root)
right.grid(column=1, row=0)

fileschooser_frame = ttk.Frame(left)
fileschooser_frame.grid(column=0, row=0, padx=10)

stampchooser_frame = ttk.Frame(fileschooser_frame)
stampchooser_frame.grid(column=0, row=0, padx=10, pady=20)

docschooser_frame = ttk.Frame(fileschooser_frame)
docschooser_frame.grid(column=0, row=1, padx=10, pady=20)

scale_frame = ttk.Frame(left)
scale_frame.grid(column=0, row=1, padx=10, pady=10)

buttons_frame = ttk.Frame(left)
buttons_frame.grid(column=0, row=2, padx=10)

# stamp details
stamp_label = ttk.Label(stampchooser_frame, text="Choose stamp image:  ")
stamp_label.grid(column=0, row=0)
stamp_path_field = ttk.Entry(stampchooser_frame, width=40)
stamp_path_field.grid(column=0, row=1)
stamp_browse = ttk.Button(stampchooser_frame, text="Browse",
                          command=stamp_chooser_event)
stamp_browse.grid(column=1, row=1, padx=10)


# docs directory
dir_label = ttk.Label(docschooser_frame, text="Choose documents directory:  ")
dir_label.grid(column=0, row=1)
dir_field = ttk.Entry(docschooser_frame, width=40)
dir_field.grid(column=0, row=2)

dir_browse = ttk.Button(docschooser_frame, text="Browse",
                        command=dir_chooser_event)
dir_browse.grid(column=1, row=2, padx=10)

# scale
scale_label = ttk.Label(scale_frame, text="scale stamp:")
scale_label.grid(column=0, row=0)
scale = ttk.Scale(scale_frame, from_=0.05, to=0.4, length=300)
scale.set(0.2)
scale.grid(column=1, row=0, padx=10)

# run
run_btn = ttk.Button(buttons_frame, text="Run",
                     command=run, width=20)
run_btn.grid(column=0, row=0, padx=10, pady=10)

# status
text = tk.Text(left)
text.grid(column=0, row=3, pady=10, padx=10)
text["width"] = 60
text["bg"] = "black"
text["fg"] = "green"

# preview
preview_btn = ttk.Button(buttons_frame, text="Preview >>",
                         command=preview, width=20)
preview_btn.grid(column=1, row=0, padx=10, pady=10)
panel = ttk.Label(right, text="")
panel.pack()

root.mainloop()
