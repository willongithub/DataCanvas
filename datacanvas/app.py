# !/usr/bin/env python3

"""General Tkinter GUI."""

import json
import os
import tkinter as tk
from shutil import copy2 as cp
# from platform import system
from threading import Thread
from tkinter import filedialog as fd
from tkinter import ttk
from tkinter.messagebox import INFO, WARNING, askokcancel, showinfo

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from PIL import Image, ImageOps, ImageTk

# import datacanvas.utils as util

WIDTH = 1280
HEIGHT = 800
SIDEBAR = 300
SHELL = 400
PADDING = 5
CANVAS = 500

TYPE = ('.jpg', '.jpeg','.png')

def main():
    """Entry point of the app."""

    DataCanvas().mainloop()


class DataCanvas(tk.Tk):
    """GUI window."""

    def __init__(self):
        super().__init__()

        self.title('DataCanvas')
        self.resizable(True, True)
        
        # machine = system()
        # if machine == 'Darwin':
        #     icon = 'datacanvas/theme/datacanvas.icns'
        # elif machine == 'Windows':
        #     icon = 'datacanvas/theme/datacanvas.ico'
        # else:
        #     icon = 'datacanvas/theme/datacanvas.xbm'
        # self.iconbitmap(icon)

        # Set theme
        self.tk.call("source", "datacanvas/theme/sun-valley.tcl")
        self.tk.call("set_theme", "light")
        # style = ttk.Style(self)
        # style.theme_use('clam')

        # Calculates location of screen centre to put the gui window.
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - WIDTH/2)
        center_y = int(screen_height/2 - HEIGHT/2)
        self.geometry(f'{WIDTH}x{HEIGHT}+{center_x}+{center_y}')

        # Create widget
        self._setup_app()

    def _setup_app(self):
        # Setup Model
        self.model = Backend()

        # Setup View
        self.view = Page(self)
        self.view.pack(fill="both", expand=True)

        # Setup Controller
        self.view.set_controller(Controller(self.model, self.view))


class Page(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.controller = None
        self.results = None
        self.modified = False
        self.canvas_plot = tk.Canvas()
        self.default = "out/task.json"

        self.parent.bind('<Key>', self._key_listener)
    
        # Create widget
        self._setup_widgets()

    def _setup_widgets(self):
        self.status = Statusbar(self)
        self.status.pack(padx=PADDING, pady=PADDING, fill='x', side='bottom')
        self.notebook = ttk.Notebook(self)
        self.notebook.pack()

        # Overview Tab
        self.overview = ttk.Frame(self.notebook)
        self.label = ttk.Labelframe(self.overview, text="Main")
        self.label.pack(padx=PADDING, pady=PADDING, side='left', fill='y')
        self.sidebar = Sidebar(self.label, self)
        self.sidebar.pack(padx=PADDING, pady=PADDING, side='left', fill='y')
        self.plot_frame = Plot(self.label)
        self.plot_frame.pack(padx=PADDING, pady=PADDING, side='top')
        self.plot_shell = Shell(self.overview)
        self.plot_shell.pack(side='left')

        # Image inspector tab
        self.inspector = ttk.Frame(self.notebook)
        self.label = ttk.Labelframe(self.inspector, text="Main")
        self.label.pack(padx=PADDING, pady=PADDING, side='left', fill='y')
        self.image_frame = Inspector(self.label, self)
        self.image_frame.pack(padx=PADDING, pady=PADDING, side='bottom')
        self.image_shell = Shell(self.inspector)
        self.image_shell.pack(side='left')
        
        self.notebook.add(self.overview, text="Overview")
        self.notebook.add(self.inspector, text="Inspector")
    
    def get_results(self):
        self.results = self.sidebar.path.get()
        self._update_content()

    def set_controller(self, Controller):
        self.controller = Controller
    
    def _key_listener(self, event):
        if event.keysym == 'Return':
            self.get_results()
        if event.keysym == 't':
            self.image_frame.toggle_image()
        if event.keysym == 'r':
            self.image_frame.remark_image()
        if event.keysym == 'a':
            self.image_frame.show_annotation()
        if event.keysym in ['Right', 'Down']:
            self.image_frame.display_image(1)
        if event.keysym in ['Left', 'Up']:
            self.image_frame.display_image(-1)
    
    # Update model shown.
    def _update_content(self):
        # Update data model
        self.controller.update()

        # Update shell area
        self.plot_shell.shell.delete('1.0', tk.END)
        self.plot_shell.insert("### Dataset Info ###")
        info = self.controller.get_info()
        self.plot_shell.insert(json.dumps(info, indent=4))
        self.plot_shell.insert("### Filter Stat ###")
        stat = self.controller.get_stat()
        for item in stat:
            self.plot_shell.insert(item)

        # Update plots area
        plot_1 = self.controller.get_hist('faces.gender')
        widget_1 = self.plot_frame.fig_1
        self._render_plot(widget_1, plot_1)

        plot_2 = self.controller.get_hist('faces.dominant_emotion')
        widget_2 = self.plot_frame.fig_2
        self._render_plot(widget_2, plot_2)

        plot_3 = self.controller.get_hist('faces.dominant_race')
        widget_3 = self.plot_frame.fig_3
        self._render_plot(widget_3, plot_3)

        # Update image inspector area
        self.image_frame.update_meta_list()

    def _render_plot(self, widget, plot):
        if self.canvas_plot:
            for child in widget.winfo_children():
                child.destroy()
        self.canvas_plot = FigureCanvasTkAgg(plot, widget)
        self.canvas_plot.draw()

        toolbar = NavigationToolbar2Tk(self.canvas_plot, widget)
        toolbar.update()

        self.canvas_plot.get_tk_widget().pack(expand=True)
    
    def show_message(self, content):
        showinfo(
            title='Message',
            message=content
        )


class Sidebar(ttk.Frame):
    def __init__(self, parent, widget):
        super().__init__(parent)
        
        # Create option list
        self.face_gender_options = ['Man', 'Woman', 'All']
        self.face_ethnicity_options = [
            'asian',
            'indian',
            'black',
            'white',
            'middle eastern',
            'latino hispanic',
            'All'
        ]
        self.face_emotion_options = [
            'angry',
            'disgust',
            'fear',
            'happy',
            'sad',
            'surprise',
            'neutral',
            'All'
        ]

        # Create option variables
        self.face_mask = tk.BooleanVar(value=True)

        self.age_lower = tk.IntVar(value=1)
        self.age_upper = tk.IntVar(value=999)

        self.gender_male = tk.BooleanVar(value=True)
        self.gender_female = tk.BooleanVar(value=True)
        self.emotion_angry = tk.BooleanVar(value=True)
        self.emotion_disgust = tk.BooleanVar(value=True)
        self.emotion_fear = tk.BooleanVar(value=True)
        self.emotion_happy = tk.BooleanVar(value=True)
        self.emotion_suprise = tk.BooleanVar(value=True)
        self.emotion_sad = tk.BooleanVar(value=True)
        self.emotion_neutral = tk.BooleanVar(value=True)
        self.ethnicity_asian = tk.BooleanVar(value=True)
        self.ethnicity_indian = tk.BooleanVar(value=True)
        self.ethnicity_african = tk.BooleanVar(value=True)
        self.ethnicity_caucasian = tk.BooleanVar(value=True)
        self.ethnicity_arabian = tk.BooleanVar(value=True)
        self.ethnicity_latino = tk.BooleanVar(value=True)
        
        self.pose_yaw_lower = tk.IntVar(value=-60)
        self.pose_yaw_upper = tk.IntVar(value=60)
        self.pose_pitch_lower = tk.IntVar(value=-60)
        self.pose_pitch_upper = tk.IntVar(value=60)
        self.pose_roll_lower = tk.IntVar(value=-60)
        self.pose_roll_upper = tk.IntVar(value=60)

        self.image_quality_lower = tk.IntVar(value=100)
        self.image_quality_upper = tk.IntVar(value=0)

        self.iris_dist_lower = tk.IntVar(value=0)
        self.iris_dist_upper = tk.IntVar(value=9999)

        self.separator = {'fill': 'x'}
        self.parent = widget

        self.path = tk.StringVar(value='assets/out/test.json')

        self._setup_widgets()

    def _setup_widgets(self):
        self.io = ttk.LabelFrame(
            self,
            text='Files',
        )
        self.io.pack(padx=PADDING, pady=PADDING, fill='x')
        ttk.Entry(self.io,
            textvariable=self.path
            ).pack(padx=PADDING, pady=PADDING)
        ttk.Button(
            self.io,
            text='Open JSON file',
            style='Accent.TButton',
            command=self._select_file
        ).pack(padx=PADDING, pady=PADDING)

        self.menu = ttk.LabelFrame(
            self,
            text='Filter',
        )
        self.menu.pack(padx=PADDING, pady=PADDING)

        self.attr_1 = ttk.LabelFrame(
            self.menu,
            text='Face',
        )
        self.attr_1.pack(padx=PADDING, pady=PADDING)
        ttk.Label(self.attr_1, text='Age').pack()
        self.filter_1 = ttk.Frame(self.attr_1)
        self.filter_1.pack()
        ttk.Entry(
            self.filter_1,
            textvariable=self.age_lower
        ).pack(pady=PADDING, side='left')
        ttk.Entry(
            self.filter_1,
            textvariable=self.age_upper
        ).pack(pady=PADDING, side='left')

        ttk.Separator(self.attr_1, orient='horizontal').pack(**self.separator)
        ttk.Label(self.attr_1, text='Gender').pack()
        self.filter_2 = ttk.Frame(self.attr_1)
        self.filter_2.pack()
        ttk.Checkbutton(
            self.filter_2,
            text='Male',
            variable=self.gender_male
        ).pack(side='left')
        ttk.Checkbutton(
            self.filter_2,
            text='Female',
            variable=self.gender_female
        ).pack(side='left')
        ttk.Separator(self.attr_1, orient='horizontal').pack(**self.separator)

        ttk.Label(self.attr_1, text='Ethnicity').pack()
        self.filter_3_1 = ttk.Frame(self.attr_1)
        self.filter_3_1.pack()
        ttk.Checkbutton(
            self.filter_3_1,
            text='Latino',
            variable=self.ethnicity_latino
        ).pack(side='left')
        ttk.Checkbutton(
            self.filter_3_1,
            text='Arabian',
            variable=self.ethnicity_arabian
        ).pack(side='left')
        ttk.Checkbutton(
            self.filter_3_1,
            text='African',
            variable=self.ethnicity_african
        ).pack(side='left')
        self.filter_3_2 = ttk.Frame(self.attr_1)
        self.filter_3_2.pack()
        ttk.Checkbutton(
            self.filter_3_2,
            text='Asian',
            variable=self.ethnicity_asian
        ).pack(side='left')
        ttk.Checkbutton(
            self.filter_3_2,
            text='Caucasian',
            variable=self.ethnicity_caucasian
        ).pack(side='left')
        ttk.Checkbutton(
            self.filter_3_2,
            text='Indian',
            variable=self.ethnicity_indian
        ).pack(side='left')
        ttk.Separator(self.attr_1, orient='horizontal').pack(**self.separator)

        ttk.Label(self.attr_1, text='Emotion').pack()
        self.filter_4_1 = ttk.Frame(self.attr_1)
        self.filter_4_1.pack()
        ttk.Checkbutton(
            self.filter_4_1,
            text='Angry',
            variable=self.emotion_angry
        ).pack(side='left')
        ttk.Checkbutton(
            self.filter_4_1,
            text='Sad',
            variable=self.emotion_sad
        ).pack(side='left')
        ttk.Checkbutton(
            self.filter_4_1,
            text='Disgust',
            variable=self.emotion_disgust
        ).pack(side='left')
        ttk.Checkbutton(
            self.filter_4_1,
            text='Fear',
            variable=self.emotion_fear
        ).pack(side='left')
        self.filter_4_2 = ttk.Frame(self.attr_1)
        self.filter_4_2.pack()
        ttk.Checkbutton(
            self.filter_4_2,
            text='Happy',
            variable=self.emotion_happy
        ).pack(side='left')
        ttk.Checkbutton(
            self.filter_4_2,
            text='Suprise',
            variable=self.emotion_suprise
        ).pack(side='left')
        ttk.Checkbutton(
            self.filter_4_2,
            text='Neutral',
            variable=self.emotion_neutral
        ).pack(side='left')
        ttk.Separator(self.attr_1, orient='horizontal').pack(**self.separator)

        self.attr_2 = ttk.LabelFrame(
            self.menu,
            text='Head',
        )
        self.attr_2.pack(padx=PADDING, pady=PADDING)
        ttk.Label(self.attr_2, text='Yaw').pack()
        self.filter_5 = ttk.Frame(self.attr_2)
        self.filter_5.pack()
        ttk.Entry(
            self.filter_5,
            textvariable=self.pose_yaw_lower
        ).pack(pady=PADDING, side='left')
        ttk.Entry(
            self.filter_5,
            textvariable=self.pose_yaw_upper
        ).pack(pady=PADDING, side='left')
        ttk.Separator(self.attr_2, orient='horizontal').pack(**self.separator)

        ttk.Label(self.attr_2, text='Pitch').pack()
        self.filter_6 = ttk.Frame(self.attr_2)
        self.filter_6.pack()
        ttk.Entry(
            self.filter_6,
            textvariable=self.pose_pitch_lower
        ).pack(pady=PADDING, side='left')
        ttk.Entry(
            self.filter_6,
            textvariable=self.pose_pitch_upper
        ).pack(pady=PADDING, side='left')
        ttk.Separator(self.attr_2, orient='horizontal').pack(**self.separator)

        ttk.Label(self.attr_2, text='Roll').pack()
        self.filter_7 = ttk.Frame(self.attr_2)
        self.filter_7.pack()
        ttk.Entry(
            self.filter_7,
            textvariable=self.pose_roll_lower
        ).pack(pady=PADDING, side='left')
        ttk.Entry(
            self.filter_7,
            textvariable=self.pose_roll_upper
        ).pack(pady=PADDING, side='left')

        ttk.Label(self.attr_2, text='Interpupillary Distance').pack()
        self.filter_9 = ttk.Frame(self.attr_2)
        self.filter_9.pack()
        ttk.Entry(
            self.filter_9,
            textvariable=self.iris_dist_lower
        ).pack(pady=PADDING, side='left')
        ttk.Entry(
            self.filter_9,
            textvariable=self.iris_dist_upper
        ).pack(pady=PADDING, side='left')

        self.attr_3 = ttk.LabelFrame(
            self.menu,
            text='Image',
        )
        self.attr_3.pack(padx=PADDING, pady=PADDING)
        ttk.Label(self.attr_3, text='IQA Score').pack()
        self.filter_8 = ttk.Frame(self.attr_3)
        self.filter_8.pack()
        ttk.Entry(
            self.filter_8,
            textvariable=self.image_quality_lower
        ).pack(pady=PADDING, side='left')
        ttk.Entry(
            self.filter_8,
            textvariable=self.image_quality_upper
        ).pack(pady=PADDING, side='left')

        ttk.Button(
            self.menu,
            text='Apply',
            style='Accent.TButton',
            command=self._get_results
        ).pack(padx=PADDING, pady=PADDING)
    
    def _get_results(self):
        self.parent.get_results()
    
    def _select_file(self):
        filetypes = (
            ('json files', '*.json'),
            ('All files', '*.*')
        )

        filepath = fd.askopenfilename(
            title='Open JSON file',
            initialdir='./',
            filetypes=filetypes
        )

        if filepath:
            showinfo(
                title='Selected',
                message=f'Open {filepath}'
            )
            self.path.set(filepath)


class Statusbar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.flag = None

        self._setup_widgets()

    def _setup_widgets(self):
        ttk.Button(
            self,
            text='New Task',
            style='Accent.TButton',
            command=self._new_task
        ).pack(padx=PADDING, pady=PADDING, side='left')
        ttk.Button(
            self,
            text='EXIT',
            style='Accent.TButton',
            command=self._exit
        ).pack(padx=PADDING, pady=PADDING, side='right')
        ttk.Button(
            self,
            text='Dark Mode',
            command=self._change_theme
        ).pack(padx=PADDING, pady=PADDING, side='right')
        # ttk.Button(
        #     self,
        #     text='Clear',
        #     command=self._clear_shell
        # ).pack(padx=PADDING, pady=PADDING, side='right')
        ttk.Button(
            self,
            text='Save',
            command=self._save
        ).pack(padx=PADDING, pady=PADDING, side='right')
        
        self.progress = ttk.Progressbar(
            self,
            orient='horizontal',
            mode='indeterminate',
            length=SIDEBAR
        )
        self.busy = ttk.Label(self, text="Busy...")
    
    def _process(self, flag):
        if flag == 'start':
            ttk.Separator(self,
            orient='vertical').pack(padx=PADDING, fill='y', side='left')
            self.progress.pack(padx=PADDING, pady=PADDING, side='left')
            self.busy.pack(padx=PADDING, pady=PADDING, side='left')
            self.progress.start(1)
        if flag == 'end':
            self.progress.stop()
            self.progress.pack_forget()
            self.busy.pack_forget()

    def _clear_shell(self):
        self.parent.shell.clear()
    
    def _save(self):
        self.parent.controller.save()
    
    def _new_task(self):
        self.parent.controller.new_task()
        
    def start_task(self):
        self.flag = self.parent.controller.task.flag
        if self.flag:
            task = AsyncProcess(self.flag)
            task.start()
            self._process('start')
            self.monitor(task)
        else:
            showinfo(message="error!")
    
    def monitor(self, thread):
        if thread.is_alive():
            self.after(5000, lambda: self.monitor(thread))
        else:
            self._process('end')
            answer = askokcancel(
                title='Note',
                message='Display new results?',
                icon=INFO
            )
            if answer:
                self.parent.sidebar.path.set(self.parent.default)
                self.parent.get_results()
            else:
                showinfo(
                    title="Info",
                    message=f"Results saved at {self.parent.default}"
                )
    
    def _change_theme(self):
        if self.tk.call("ttk::style", "theme", "use") == "sun-valley-dark":
            self.tk.call("set_theme", "light")
            self.parent.plot_shell.shell.config(bg='gray90', fg='black')
            self.parent.image_shell.shell.config(bg='gray90', fg='black')
            self.parent.controller.change_theme('light')
        else:
            self.tk.call("set_theme", "dark")
            self.parent.plot_shell.shell.config(bg='gray20', fg='lime green')
            self.parent.image_shell.shell.config(bg='gray20', fg='lime green')
            self.parent.controller.change_theme('dark')
        self.parent.get_results()
    
    def _exit(self):
        if self.parent.modified:
            answer = askokcancel(
                title='Confirmation',
                message='Leave without saving?',
                icon=WARNING
            )
            if answer:
                exit()
            else:
                self.parent.controller.save()
        else:
            exit()


class Plot(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self._setup_widgets()

    def _setup_widgets(self):
        self.canvas = ttk.Notebook(
            self,
            width=WIDTH-SHELL-SIDEBAR,
            height=HEIGHT
        )
        self.canvas.pack(padx=PADDING, side='left')

        # One plot for each tab
        self.fig_1 = ttk.Frame(self.canvas)
        self.fig_1.pack(side='left', fill='y')
        self.canvas.add(self.fig_1, text='Fig 1')
        self.fig_2 = ttk.Frame(self.canvas)
        self.fig_2.pack(side='left', fill='y')
        self.canvas.add(self.fig_2, text='Fig 2')
        self.fig_3 = ttk.Frame(self.canvas)
        self.fig_3.pack(side='left', fill='y')
        self.canvas.add(self.fig_3, text='Fig 3')


class Inspector(ttk.Frame):
    def __init__(self, parent, tab):
        super().__init__(parent)
        
        self.parent = tab
        self.meta_list = None
        self.toggle = False
        self.remark = tk.StringVar(value='Enter remark here')
        self.img_pointer = 0
        self.MAX_SIZE = (CANVAS - PADDING, CANVAS + SHELL - PADDING)

        self._setup_widgets()

    def _setup_widgets(self):
        self.task = ttk.Frame(self)
        self.task.pack(side='bottom')

        self.annotation = ttk.Label(self,
            text='',
            padding=(PADDING, PADDING))
        self.annotation.pack(side='bottom')
        
        self.canvas = tk.Canvas(self, height=CANVAS, width=CANVAS+SHELL)
        self.canvas.pack(padx=PADDING, pady=PADDING)
        
        ttk.Button(
            self.task,
            style='Accent.TButton',
            command=lambda : self.display_image(-1),
            text="Prev").pack(padx=PADDING, pady=PADDING, side='left')
        ttk.Button(
            self.task,
            style='Accent.TButton',
            command=lambda : self.display_image(1),
            text="Next"
            ).pack(padx=PADDING, pady=PADDING, side='left')
        ttk.Button(
            self.task,
            command=self.show_annotation,
            text="Annotation"
            ).pack(padx=PADDING, pady=PADDING, side='left')
        ttk.Button(
            self.task,
            command=self.toggle_image,
            text="Toggle"
            ).pack(padx=PADDING, pady=PADDING, side='left')
        ttk.Button(
            self.task,
            command=self.remark_image,
            text="Remark"
            ).pack(padx=PADDING, pady=PADDING, side='left')
        ttk.Entry(self.task,
            textvariable=self.remark
            ).pack(padx=PADDING, pady=PADDING, side='left')

    def display_image(self, offset=0):
        try:
            self.img_pointer += offset
            if self.img_pointer < 0:
                self.img_pointer = 0
            self.file = self.meta_list.iloc[self.img_pointer]['file']
        except ValueError:
            showinfo(
                title='Note',
                message='Out of Range.'
            )
            self.img_pointer -= offset
            return
        self.img = Image.open(self.file)
        self.annotation.config(
            text = f"File: {self.file}  |  Resolution: {self.img.size}")
        self.img = ImageTk.PhotoImage(ImageOps.pad(self.img, self.MAX_SIZE))
        self.canvas.create_image(
            (CANVAS+SHELL)/2, CANVAS/2,
            image=self.img)
        self.display_meta(self.img_pointer)
    
    def update_meta_list(self):
        self.meta_list = self.parent.controller.get_model()
        if self.meta_list.shape[0] > 0:
            self.display_image()

    def display_meta(self, pointer):
        self.parent.image_shell.shell.delete('1.0', tk.END)
        meta = self.parent.controller.get_raw()[pointer]
        self.parent.image_shell.insert(json.dumps(meta, indent=4))

    def show_annotation(self):
        # TODO: Show detection annotation
        pass

    def remark_image(self):
        self.parent.image_shell.insert(f"> Remark: {self.remark.get()}")
        self.parent.controller.remark_image(
            self.img_pointer, self.remark.get())

    def toggle_image(self):
        self.toggle = not self.toggle
        self.parent.image_shell.insert(f"> Toggle: {self.toggle}")
        self.parent.controller.toggle_image(
            self.img_pointer, self.toggle)


class Shell(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self._setup_widgets()

    def _setup_widgets(self):
        self.label = ttk.LabelFrame(self, text="Metadata")
        self.shell = tk.Text(
            self.label,
            # bg='gray20',
            # fg='lime green',
            bg='gray90',
            fg='black',
            height=HEIGHT,
            width=SHELL
        )
        self.label.pack(padx=PADDING, pady=PADDING, side='left')
        self.shell.pack(padx=PADDING, pady=PADDING)

    def insert(self, output):
        self.shell.insert(tk.INSERT, f'{output}\n')
        self.shell.see("end")

    def clear(self):
        answer = askokcancel(
            title='Confirmation',
            message='CLI outout will be removed.',
            icon=WARNING
        )
        if answer:
            self.shell.delete('1.0', tk.END)
            showinfo(
                title='Status',
                message='CLI output all clear.'
            )


class Task(tk.Toplevel):
    def __init__(self, parent, widget):
        super().__init__(parent)

        self.parent = widget
        self.flag = None
        self.bind('<Return>', self._return_listener)

        self.title('New Task')
        self.resizable(False, False)

        # Calculates location of screen centre to put the gui window.
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - CANVAS/2)
        center_y = int(screen_height/2 - CANVAS/2)
        self.geometry(f'{SIDEBAR}x{CANVAS}+{center_x}+{center_y}')

        self.confidence = tk.DoubleVar(value=0.7)
        self.gender = tk.BooleanVar(value=True)
        self.ethnicity = tk.BooleanVar(value=True)
        self.emotion = tk.BooleanVar(value=True)
        self.age = tk.BooleanVar(value=True)
        self.pose = tk.BooleanVar(value=True)
        self.quality = tk.BooleanVar(value=True)

        self.folder = tk.StringVar(value="assets/data/")

        # Create widget
        self._setup_window()

    def _setup_window(self):
        self.io = ttk.LabelFrame(
            self,
            text='Image Folder',
        )
        self.io.pack(padx=PADDING, pady=PADDING, fill='x')
        ttk.Entry(self.io,
            textvariable=self.folder
            ).pack(padx=PADDING, pady=PADDING)
        ttk.Button(
            self.io,
            text='Select Image Folder',
            style='Accent.TButton',
            command=self._select_folder
        ).pack(padx=PADDING, pady=PADDING)

        self.frame = ttk.Labelframe(
            self,
            text='Face Detection'
        )
        self.frame.pack(
            padx=PADDING, pady=PADDING,
            ipadx=PADDING, ipady=PADDING, fill='x')
        ttk.Label(
            self.frame,
            text='Confidence Level:',
            padding=PADDING).pack(padx=PADDING, pady=PADDING)
        ttk.Spinbox(
            self.frame,
            from_=0.0,
            to=1.0,
            textvariable=self.confidence
        ).pack(padx=PADDING, pady=PADDING)
        ttk.Separator(
            self.frame, orient='horizontal').pack(fill='x', pady=PADDING)

        ttk.Label(
            self.frame,
            text='Face Attributes:',
            padding=PADDING).pack(padx=PADDING, pady=PADDING)
        
        self.attr_1 = ttk.Frame(self.frame)
        self.attr_1.pack()
        ttk.Checkbutton(
            self.attr_1,
            text='Age',
            variable=self.age
        ).pack()
        ttk.Checkbutton(
            self.attr_1,
            text='Gender',
            variable=self.gender
        ).pack()
        ttk.Checkbutton(
            self.attr_1,
            text='Ethnicity',
            variable=self.ethnicity
        ).pack()
        ttk.Checkbutton(
            self.attr_1,
            text='Emotion',
            variable=self.emotion
        ).pack()

        self.attr_2 = ttk.Frame(self.frame)
        self.attr_2.pack()
        ttk.Checkbutton(
            self.attr_2,
            text='Head Pose',
            variable=self.pose
        ).pack()
        ttk.Checkbutton(
            self.attr_2,
            text='Image Quality',
            variable=self.quality
        ).pack()

        ttk.Button(
            self,
            text='Run',
            style='Accent.TButton',
            command=self._run
        ).pack(padx=PADDING, pady=PADDING, side='bottom')
    
    def _return_listener(self, _):
        self._run()

    def _select_folder(self):
        filepath = fd.askdirectory(
            title='Open image folder',
            initialdir='./'
        )
        if filepath:
            showinfo(
                title='Selected',
                message=f'Open {filepath}'
            )
            self.folder.set(filepath)

    def _run(self):
        self.flag = {
            'folder': self.folder.get(),
            'confidence': self.confidence.get(),
            'age': self.age.get(),
            'gender': self.gender.get(),
            'ethnicity': self.ethnicity.get(),
            'emotion': self.emotion.get(),
            'pose': self.pose.get(),
            'quality': self.quality.get()
        }

        answer = askokcancel(
            title='Confirmation',
            message='Start new task?',
            icon=INFO
        )
        if answer:
            self.destroy()
            self.parent.view.status.start_task()


class AsyncProcess(Thread):
    def __init__(self, flag):
        super().__init__()
        self.flag = flag

    def run(self) -> None:
        # TODO: Link worker
        showinfo(message=self.flag)


class Backend:
    def __init__(self) -> None:
        self._model = None
        self._raw = None
        self._info = None
        self._files = None
        self._results = None
    
    @property
    def model(self) -> str:
        return self._model
    
    @property
    def raw(self) -> str:
        return self._raw
    
    @property
    def files(self) -> str:
        return self._files
    
    @property
    def results(self) -> str:
        return self._results
    
    @property
    def info(self) -> str:
        return self._info

    @files.setter
    def files(self, path) -> None:
        self._files = path
    
    @results.setter
    def results(self, path) -> None:
        self._results = path
    
    @model.setter
    def model(self, model) -> None:
        self._model = model

    def load_results(self) -> None:
        if os.path.exists(self._results):
            with open(self._results) as f:
                data = json.load(f)
            self._model = pd.json_normalize(data["output"])
            self._raw = data["output"]
            self._info = data["metadata"]
            self._files = data["metadata"]["files"]

    def save(self, meta) -> None:
        records = json.loads(self.model.to_json(orient="records"))
        file = {
            "metadata": meta,
            "output": records
        }
        path = os.path.join(self.results, "output.json")
        with open(path, "w") as f:
            f.write(json.dumps(file, indent=4))
        
        answer = askokcancel(
            title='New Dataset',
            message='Create new dataset?',
            icon=INFO
        )
        if answer:
            dest = self.results
            for image in self._raw:
                source = image["file"]
                cp(source, dest)

        msg = f"Result saved at {self.results}"

        return msg


class Controller:
    def __init__(self, model, view) -> None:
        self.model = model
        self.view = view
        self.meta = None

        # Filter threshold
        self.yaw = None
        self.pitch = None
        self.roll = None
        self.gender = None
        self.emotion = None
        self.ethnicity = None
        self.age = None
        self.quality = None
        self.confidence = None
    
    def load(self) -> None:
        try:
            self.model.load_results()
        except Exception as error:
            self.view.show_message(error)
    
    def update(self) -> None:
        self.model.results = self.view.results
        self.load()

        self.apply_filter()
    
    def apply_filter(self):
        self.quality = self.view.sidebar.image_quality_var.get()

        self.age = self.view.sidebar.age_var.get()
        self.gender = [self.view.sidebar.gender_var.get()]
        self.ethnicity = [self.view.sidebar.ethnicity_var.get()]
        self.emotion = [self.view.sidebar.emotion_var.get()]

        self.yaw = self.view.sidebar.pose_yaw.get()
        self.pitch = self.view.sidebar.pose_pitch.get()
        self.roll = self.view.sidebar.pose_roll.get()

        df = self.model.model
        self.model.model = df[
            (df['quality'] < self.quality) &
            (df['faces.age'] < self.age) &
            (df['faces.gender'].isin(self.gender)) &
            (df['faces.dominant_race'].isin(self.ethnicity)) &
            (df['faces.dominant_emotion'].isin(self.emotion)) &
            (df['pose.yaw'] < self.yaw) &
            (df['pose.pitch'] < self.pitch) &
            (df['pose.roll'] < self.roll)
        ]
        self.meta = {
            'folder': self.model.files,
            'count': self.model.model.shape[0]
        }
        
        self.view.modified = True
    
    def new_task(self):
        self.task = Task(self.view.parent, self)
    
    def save(self) -> None:
        """Save results."""
        path = self._select_folder()
        if path:
            self.model._results = path
            try:               
                msg = self.model.save(self.meta)
                self.view.modified = False
                self.view.show_message(msg)
            except Exception as error:
                self.view.show_message(error)

    def get_files(self):
        return self.model.files

    def get_results(self):
        return self.model.results
    
    def get_model(self):
        return self.model.model
    
    def get_raw(self):
        return self.model.raw

    def toggle_image(self, pointer, toggle):
        df = self.model.model
        if 'toggle' not in df.columns:
            df['toggle'] = False
        df.iat[pointer, df.columns.get_loc("toggle")] = toggle

    def remark_image(self, pointer, remark):
        df = self.model.model
        if 'remark' not in df.columns:
            df['remark'] = 'NA'
        df.iat[pointer, df.columns.get_loc("remark")] = remark

    def get_info(self):
        return self.model.info
    
    def get_stat(self):
        try:
            file = int(self.model.model["file"].count())
            age = int(self.model.model["faces.age"].mean())
            gender = self.model.model["faces.gender"].value_counts(normalize=True).to_string()
            ethnicity = self.model.model["faces.dominant_race"].value_counts(normalize=True).to_string()
            emotion = self.model.model["faces.dominant_emotion"].value_counts(normalize=True).to_string()
            stat = [
                f"> File count:\n{file}",
                f"> Average age:\n{age}",
                f"> Gender:\n{gender}",
                f"> Ethnicity:\n{ethnicity}",
                f"> Emotion:\n{emotion}"
            ]
        except:
            file = int(self.model.model["file"].count())
            stat = [f"> File count:\n{file}"]
        return stat

    def change_theme(self, theme):
        if theme == 'light':
            plt.style.use("fivethirtyeight")
        if theme == 'dark':
            plt.style.use("dark_background")
    
    def _select_folder(self):
        filepath = fd.askdirectory(
            title='Select save folder.',
            initialdir='./'
        )
        if filepath:
            return filepath
    
    # Plots for data model overview
    # TODO: Build plots
    def get_boxplot(self):
        fig = plt.figure()
        return fig
    
    def get_hist(self, attr):
        fig, ax = plt.subplots()

        data = self.get_model()

        sns.histplot(
            data,
            x="quality",
            hue=attr,
            multiple="stack"
        )

        return fig