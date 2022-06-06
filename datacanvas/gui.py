# !/usr/bin/env python3

"""General Tkinter GUI."""

import json
import os
import tkinter as tk
from platform import system
from tkinter import filedialog as fd
from tkinter import ttk
from tkinter.messagebox import WARNING, askokcancel, showinfo

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from PIL import Image, ImageOps, ImageTk

import datacanvas.utils as util

WIDTH = 1280
HEIGHT = 800
SIDEBAR = 100
SHELL = 400
PADDING = 5
CANVAS = 500

TYPE = ('.jpg', '.jpeg','.png')


class DataCanvas(tk.Tk):
    """GUI window."""

    def __init__(self):
        super().__init__()

        self.title('DataCanvas')
        self.resizable(True, True)
        
        # machine = system()
        # if machine == 'Darwin':
        #     icon = 'datacanvas/datacanvas.icns'
        # elif machine == 'Windows':
        #     icon = 'datacanvas/datacanvas.ico'
        # else:
        #     icon = 'datacanvas/datacanvas.xbm'
        # self.iconbitmap(icon)

        # Set theme
        self.tk.call("source", "assets/theme/sun-valley.tcl")
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
        self.model.results = 'assets/test.json'

        # Setup View
        self.view = Page(self)
        self.view.pack(fill="both", expand=True)

        # Setup Controller
        self.view.set_controller(Controller(self.model, self.view))


class Page(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.controller = None
        self.results = None
        self.selected = False
        self.canvas_plot = tk.Canvas()
    
        # Create widget
        self._setup_widgets()

    def _setup_widgets(self):
        Statusbar(self).pack(padx=PADDING, pady=PADDING, fill='x', side='bottom')
        self.notebook = ttk.Notebook(self)
        self.notebook.pack()

        # Overview Tab
        self.overview = ttk.Frame(self.notebook)
        self.label = ttk.Labelframe(self.overview, text="Main")
        self.label.pack(padx=PADDING, pady=PADDING, side='left', fill='y')
        self.sidebar = Sidebar(self.label)
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
        if self.sidebar.path:
            self.results = self.sidebar.path
            self.selected = True
        else:
            self.results = self.controller.get_results()
        
        self._update_content()

    def set_controller(self, Controller):
        self.controller = Controller
    
    # Update model shown.
    def _update_content(self):
        # Update data model
        self.controller.update()

        # Update shell area
        self.plot_shell.insert("### Dataset Info ###")
        info = self.controller.get_info()
        self.plot_shell.insert(json.dumps(info, indent=4))
        self.plot_shell.insert("### Simple Stat ###")
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


class Sidebar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.path = None
        
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
        
        self.pose_yaw = tk.DoubleVar(value=90)
        self.pose_pitch = tk.DoubleVar(value=90)
        self.pose_roll = tk.DoubleVar(value=90)

        self.gender_var = tk.StringVar()
        self.emotion_var = tk.StringVar()
        self.ethnicity_var = tk.StringVar()
        self.age_var = tk.IntVar(value=999)

        self.image_quality_var = tk.DoubleVar(value=100)
        self.confidence_var = tk.DoubleVar(value=80.0)

        self.separator = {'fill': 'x'}

        self._setup_widgets()

    def _setup_widgets(self):
        self.io = ttk.LabelFrame(
            self,
            text='Files',
        )
        self.io.pack(padx=PADDING, pady=PADDING, fill='x')
        ttk.Button(
            self.io,
            text='Open output JSON file',
            command=self._select_file
        ).pack(padx=PADDING, pady=PADDING)

        self.menu = ttk.LabelFrame(
            self,
            text='Filter',
        )
        self.menu.pack(padx=PADDING, pady=PADDING)

        self.attr_0 = ttk.LabelFrame(
            self.menu,
            text='Detection',
        )
        self.attr_0.pack(padx=PADDING, pady=PADDING)
        ttk.Label(self.attr_0, text='Confidence Level', padding=5).pack()
        ttk.Spinbox(
            self.attr_0,
            from_=0.0,
            to=1.0,
            textvariable=self.confidence_var
        ).pack()

        self.attr_1 = ttk.LabelFrame(
            self.menu,
            text='Face',
        )
        self.attr_1.pack(padx=PADDING, pady=PADDING)
        ttk.Label(self.attr_1, text='Age', padding=5).pack()
        ttk.Spinbox(
            self.attr_1,
            from_=1,
            to=999,
            textvariable=self.age_var
        ).pack()
        ttk.Separator(self.attr_1, orient='horizontal').pack(**self.separator)
        ttk.Label(self.attr_1, text='Gender', padding=5).pack()
        ttk.OptionMenu(
            self.attr_1,
            self.gender_var,
            self.face_gender_options[-1],
            *self.face_gender_options,
        ).pack()
        ttk.Separator(self.attr_1, orient='horizontal').pack(**self.separator)
        ttk.Label(self.attr_1, text='Ethnicity', padding=5).pack()
        ttk.OptionMenu(
            self.attr_1,
            self.ethnicity_var,
            self.face_ethnicity_options[-1],
            *self.face_ethnicity_options,
        ).pack()
        ttk.Separator(self.attr_1, orient='horizontal').pack(**self.separator)
        ttk.Label(self.attr_1, text='Emotion', padding=5).pack()
        ttk.OptionMenu(
            self.attr_1,
            self.emotion_var,
            self.face_emotion_options[-1],
            *self.face_emotion_options,
        ).pack()

        self.attr_2 = ttk.LabelFrame(
            self.menu,
            text='Head',
        )
        self.attr_2.pack(padx=PADDING, pady=PADDING)
        ttk.Label(self.attr_2, text='Yaw', padding=5).pack()
        ttk.Spinbox(
            self.attr_2,
            from_=0,
            to=90,
            textvariable=self.pose_yaw
        ).pack()
        ttk.Separator(self.attr_2, orient='horizontal').pack(**self.separator)
        ttk.Label(self.attr_2, text='Pitch', padding=5).pack()
        ttk.Spinbox(
            self.attr_2,
            from_=0,
            to=90,
            textvariable=self.pose_pitch
        ).pack()
        ttk.Separator(self.attr_2, orient='horizontal').pack(**self.separator)
        ttk.Label(self.attr_2, text='Roll', padding=5).pack()
        ttk.Spinbox(
            self.attr_2,
            from_=0,
            to=90,
            textvariable=self.pose_roll
        ).pack()

        self.attr_3 = ttk.LabelFrame(
            self.menu,
            text='Image',
        )
        self.attr_3.pack(padx=PADDING, pady=PADDING)
        ttk.Label(self.attr_3, text='IQA Score', padding=5).pack()
        ttk.Spinbox(
            self.attr_3,
            from_=100,
            to=0,
            textvariable=self.image_quality_var
        ).pack()
    
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
            self.path = filepath


class Statusbar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self._setup_widgets()

    def _setup_widgets(self):
        ttk.Button(
            self,
            text='Apply Filter',
            style='Accent.TButton',
            command=self._get_result
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
        
        # TODO: Implement pregressbar with async
        self.progress = ttk.Progressbar(
            self,
            orient='horizontal',
            mode='indeterminate',
            length=SIDEBAR
        )
    
    def _process(self, flag):
        if flag == 'start':
            ttk.Separator(self,
            orient='vertical').pack(padx=PADDING, fill='y', side='left')
            self.progress.pack(padx=PADDING, pady=PADDING, side='left')
            self.progress.start
        if flag == 'end':
            self.progress.stop
            self.process.pack_forget()

    def _clear_shell(self):
        self.parent.shell.clear()
    
    def _save(self):
        self.parent.controller.save()
    
    def _get_result(self):
        self.parent.get_results()
    
    def _change_theme(self):
        if self.tk.call("ttk::style", "theme", "use") == "sun-valley-dark":
            self.tk.call("set_theme", "light")
            self.parent.plot_shell.shell.config(bg='gray90', fg='black')
            self.parent.image_shell.shell.config(bg='gray90', fg='black')
        else:
            self.tk.call("set_theme", "dark")
            self.parent.plot_shell.shell.config(bg='gray20', fg='lime green')
            self.parent.image_shell.shell.config(bg='gray20', fg='lime green')
    
    def _exit(self):
        # TODO: Check fale save flag
        answer = askokcancel(
            title='Confirmation',
            message='Are you sure?',
            icon=WARNING
        )
        if answer:
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
        self.remark = tk.StringVar(value='Enter comment here')
        self.img_pointer = -1
        self.MAX_SIZE = (CANVAS - PADDING, CANVAS + SHELL - PADDING)

        self._setup_widgets()

    def _setup_widgets(self):
        self.task = ttk.Frame(self)
        self.task.pack(side='bottom')

        # ttk.Separator(self, orient='horizontal').pack(fill='x', side='bottom')
        self.annotation = ttk.Label(self,
            text='',
            padding=(PADDING, PADDING))
        self.annotation.pack(side='bottom')
        
        self.canvas = tk.Canvas(self, height=CANVAS, width=CANVAS+SHELL)
        self.canvas.pack(padx=PADDING, pady=PADDING)
        
        ttk.Button(
            self.task,
            command=self.toggle_image,
            text="Delete"
            ).pack(padx=PADDING, pady=PADDING, side='left')
        ttk.Button(
            self.task,
            command=lambda : self.display_image(-1),
            text="Prev").pack(padx=PADDING, pady=PADDING, side='left')
        ttk.Button(
            self.task,
            command=lambda : self.display_image(1),
            text="Next"
            ).pack(padx=PADDING, pady=PADDING, side='left')
        ttk.Button(
            self.task,
            command=lambda : self.show_mask(self.remark.get()),
            text="Mask"
            ).pack(padx=PADDING, pady=PADDING, side='left')
        ttk.Button(
            self.task,
            command=lambda : self.save_remark(self.remark.get()),
            text="Comment"
            ).pack(padx=PADDING, pady=PADDING, side='left')
        ttk.Entry(self.task,
            textvariable=self.remark
            ).pack(padx=PADDING, pady=PADDING, side='left')

    def display_image(self, offset):
        try:
            self.img_pointer += offset
            if self.img_pointer < 0:
                self.img_pointer = 0
            self.file = self.meta_list.loc[self.img_pointer]['file']
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
        self.display_image(1)

    def display_meta(self, pointer):
        self.parent.image_shell.shell.delete('1.0', tk.END)
        meta = self.parent.controller.get_raw()[pointer]
        self.parent.image_shell.insert(json.dumps(meta, indent=4))

    def show_mask(self):
        # TODO: show detection mask
        pass

    def save_remark(self, remark):
        self.parent.parent.controller.save_remark(remark)

    def toggle_image(self):
        self.parent.parent.controller.toggle_image()


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

    def load_results(self) -> None:
        if os.path.exists(self._results):
            with open(self._results) as f:
                data = json.load(f)
            self._model = pd.json_normalize(data["output"])
            self._raw = data["output"]
            self._info = data["metadata"]
            self._files = data["metadata"]["files"]

    def run(self, **flag) -> None:
        self._model = util.run(flag)

    def save(self, path, model) -> None:
        util.save(path, model)
        msg = f"Result saved at {path}"
        return msg


class Controller:
    def __init__(self, model, view) -> None:
        self.model = model
        self.view = view

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

        self.load()
    
    def run(self, **flag) -> None:
        self.view.run(flag)
    
    def load(self) -> None:
        try:
            self.model.load_results()
        except Exception as error:
            self.view.show_message(error)
    
    def update(self) -> None:
        if self.view.selected:
            self.model.path = self.view.results
            self.load()
        
        self.yaw = self.view.sidebar.pose_yaw.get()
        self.pitch = self.view.sidebar.pose_pitch.get()
        self.roll = self.view.sidebar.pose_roll.get()
        self.age = self.view.sidebar.age_var.get()
        self.quality = self.view.sidebar.image_quality_var.get()
        self.confidence = self.view.sidebar.confidence_var.get()

        self.gender = self.view.sidebar.gender_var.get()
        self.ethnicity = self.view.sidebar.ethnicity_var.get()
        self.emotion = self.view.sidebar.emotion_var.get()

        self.apply_filter()
    
    def save(self, file) -> None:
        """Save results."""

        try:
            msg = self.model.save(file)
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

    def apply_filter(self):
        # TODO: Return filtered model
        return self.model.model

    def toggle_image(self):
        # TODO: Toggle image in the JSON file
        pass

    def save_remark(self, remark):
        # TODO: Save image remark in the JSON file
        pass

    def get_info(self):
        return self.model.info
    
    def get_stat(self):
        # TODO: Return stat of the model
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
        return stat

    # Plots for data model overview
    # TODO: Build plots
    def get_boxplot(self):
        fig = plt.figure()
        return fig
    
    def get_hist(self, attr):
        fig, ax = plt.subplots()

        data = self.apply_filter()

        sns.histplot(
            data,
            x="quality",
            hue=attr,
            multiple="stack"
        )

        return fig