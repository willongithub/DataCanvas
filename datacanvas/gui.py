# !/usr/bin/env python3

"""General Tkinter GUI."""

import json
import os
import tkinter as tk
from platform import system
from tkinter import filedialog as fd
from tkinter import ttk
from tkinter.messagebox import WARNING, askokcancel, showinfo
from tkinter.scrolledtext import ScrolledText

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from PIL import Image, ImageTk

import datacanvas.utils as util

WIDTH = 1280
HEIGHT = 800
SIDEBAR = 200
SHELL = 400
PADDING = 10
CANVAS = 700


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
        self.model.path = 'assets/test.json'

        # Setup View
        self.view = Page(self)
        self.view.pack(fill="both", expand=True)

        # Setup Controller
        self.view.set_controller(Controller(self.model, self.view))


class Page(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.controller = None
        self.file = None
    
        # Create widget
        self._setup_widgets()

    def _setup_widgets(self):
        Control(self).pack(side='bottom')
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(padx=PADDING, pady=PADDING, side='left')

        self.canvas_plot = tk.Canvas()

        # Shell style output area
        self.shell = ScrolledText(
            self,
            bg='gray20',
            fg='lime green',
            height=HEIGHT
        )
        self.shell.pack(side='left')

        # Tabs
        self.overview_tab = Tab(self, "overview")
        self.selector_tab = Tab(self, "selector")
        
        self.notebook.add(self.overview_tab, text="Overview")
        self.notebook.add(self.selector_tab, text="Selector")
    
    def get_results(self):
        if self.overview_tab.sidebar.path:
            self.file = self.overview_tab.sidebar.path
        
        self._update_content()

    def set_controller(self, controller):
        self.controller = controller
    
    # Draw plot on canvas.
    def _update_content(self):
        self.controller.update()
        info = self.controller.read_info()

        self._insert_shell('in progress...')
        self._insert_shell('=========================')
        # for item in info:
        #     self._insert_shell(item)
        self._insert_shell(info)
        self._insert_shell('\n\n')

        plot_1 = self.controller.get_hist('faces.gender')
        widget_1 = self.overview_tab.mainframe.fig_1
        self._render_plot(widget_1, plot_1)

        plot = self.controller.get_hist('faces.dominant_emotion')
        widget = self.overview_tab.mainframe.fig_2
        self._render_plot(widget, plot)

        plot = self.controller.get_hist('faces.dominant_race')
        widget = self.overview_tab.mainframe.fig_3
        self._render_plot(widget, plot)

    def _insert_shell(self, output):
        self.shell.insert(tk.INSERT, f' {output}\n')
        self.shell.see("end")

    def _clear_shell(self):
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

    def _render_plot(self, widget, plot):
        if self.canvas_plot:
            for child in widget.winfo_children():
                child.destroy()
        self.canvas_plot = FigureCanvasTkAgg(plot, widget)
        self.canvas_plot.draw()

        toolbar = NavigationToolbar2Tk(self.canvas_plot, widget)
        toolbar.update()

        self.canvas_plot.get_tk_widget().pack(expand=True)


class Tab(ttk.Frame):
    def __init__(self, parent, content):
        super().__init__(parent)
        
        # Create widget
        self._setup_widgets(content)

    def _setup_widgets(self, content):      
        # Child widget
        if content == "overview":
            self.sidebar = Sidebar(self)
            self.sidebar.pack(side='left')
            self.mainframe = Plot(self)
            self.mainframe.pack(side='bottom', padx=PADDING, pady=PADDING)
        if content == "selector":
            self.mainframe = Selector(self)
            self.mainframe.pack(side='bottom', padx=PADDING, pady=PADDING)


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
            'all'
        ]
        self.face_emotion_options = [
            'angry',
            'disgust',
            'fear',
            'happy',
            'sad',
            'surprise',
            'neutral',
            'all'
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
        self.io.pack(padx=PADDING, pady=PADDING)
        ttk.Button(
            self.io,
            text='Select JSON file',
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
            self.face_gender_options[0],
            *self.face_gender_options,
        ).pack()
        ttk.Separator(self.attr_1, orient='horizontal').pack(**self.separator)
        ttk.Label(self.attr_1, text='Ethnicity', padding=5).pack()
        ttk.OptionMenu(
            self.attr_1,
            self.ethnicity_var,
            self.face_ethnicity_options[0],
            *self.face_ethnicity_options,
        ).pack()
        ttk.Separator(self.attr_1, orient='horizontal').pack(**self.separator)
        ttk.Label(self.attr_1, text='Emotion', padding=5).pack()
        ttk.OptionMenu(
            self.attr_1,
            self.emotion_var,
            self.face_emotion_options[0],
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


class Control(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self._setup_widgets(parent)

    def _setup_widgets(self, parent):
        ttk.Button(
            self,
            text='Dark Mode',
            command=self._change_theme
        ).pack(padx=PADDING, pady=PADDING, side='left')
        # ttk.Button(
        #     self,
        #     text='Exit',
        #     command=self._exit
        # ).pack(padx=PADDING, pady=PADDING, side='left')
        ttk.Button(
            self,
            text='Clear',
            command=self._clear_shell
        ).pack(padx=PADDING, pady=PADDING, side='left')
        ttk.Button(
            self,
            text='Apply',
            style='Accent.TButton',
            command=parent.get_results
        ).pack(padx=PADDING, pady=PADDING, side='left')
        
        self.progress = ttk.Progressbar(
            self,
            orient='horizontal',
            mode='indeterminate',
            length=SIDEBAR
        )
    
    def _process(self, flag):
        if flag == 'start':
            self.progress.pack(padx=PADDING, pady=PADDING, side='left')
            self.progress.start
        if flag == 'end':
            self.progress.stop
            self.process.pack_forget()

    def _clear_shell(self):
        answer = askokcancel(
            title='Confirmation',
            message='CLI outout will be removed.',
            icon=WARNING
        )
        if answer:
            self.parent.shell.delete('1.0', tk.END)
            showinfo(
                title='Status',
                message='CLI output all clear.'
            )
    
    def _change_theme(self):
        if self.tk.call("ttk::style", "theme", "use") == "sun-valley-dark":
            # Set light theme
            self.tk.call("set_theme", "light")
        else:
            # Set light theme
            self.tk.call("set_theme", "dark")
    
    def _exit(self):
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
        self.canvas.pack(pady=PADDING, side='left')

        # Tabs for plots
        self.fig_1 = ttk.Frame(self.canvas)
        self.fig_1.pack(side='left', fill='y')
        self.canvas.add(self.fig_1, text='Fig 1')
        self.fig_2 = ttk.Frame(self.canvas)
        self.fig_2.pack(side='left', fill='y')
        self.canvas.add(self.fig_2, text='Fig 2')
        self.fig_3 = ttk.Frame(self.canvas)
        self.fig_3.pack(side='left', fill='y')
        self.canvas.add(self.fig_3, text='Fig 3')


class Selector(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.image_list = [
            ImageTk.PhotoImage(Image.open("assets/image/img_1.jpg").resize((CANVAS, CANVAS))),
            ImageTk.PhotoImage(Image.open("assets/image/img_2.jpg").resize((CANVAS, CANVAS))),
            ImageTk.PhotoImage(Image.open("assets/image/img_3.jpg").resize((CANVAS, CANVAS)))
        ]

        self.count = 0

        self._setup_widgets()

    def _setup_widgets(self):
        self.control = ttk.Frame(self)
        self.control.pack(side='bottom')
        self.image = ttk.LabelFrame(self, text='Image Viwer')
        self.image.pack()

        self.annotation = ttk.Label(self.image, text='Dog/Cat')
        self.annotation.pack(padx=PADDING, pady=PADDING, side='bottom')
        self.canvas = tk.Canvas(self.image, height=CANVAS, width=CANVAS)
        self.canvas.pack(padx=PADDING, pady=PADDING)

        self.canvas.create_image(
            CANVAS/2, CANVAS/2,
            image=self.image_list[self.count])
        
        self.button_back = ttk.Button(
            self.control,
            # command=self._back,
            state=tk.DISABLED,
            text="  <  ")
        
        self.button_forward = ttk.Button(
            self.control,
            command=self._forward,
            text="  >  ")
        
        self.button_delete = ttk.Button(
            self.control,
            command=self._delete,
            state=tk.DISABLED,
            text="  x  ")
        
        self.button_back.pack(padx=PADDING, pady=PADDING, side='left')
        self.button_forward.pack(padx=PADDING, pady=PADDING, side='left')
        self.button_delete.pack(padx=PADDING, pady=PADDING, side='left')
    
    def _delete(self):
        pass

    def _forward(self):
        self.canvas.delete('all')
        self.count += 1

        self.canvas.create_image(CANVAS/2, CANVAS/2, image=self.image_list[self.count])

        if self.count > 0:
            self.button_back.pack_forget()
            self.button_forward.pack_forget()
            self.button_back = ttk.Button(
                self.control,
                command=self._back,
                text="  <  ")
            self.button_forward = ttk.Button(
                self.control,
                command=self._forward,
                text="  >  ")
            self.button_back.pack(padx=PADDING, pady=PADDING, side='left')
            self.button_forward.pack(padx=PADDING, pady=PADDING, side='left')

        if self.count == 2:
            self.button_back.pack_forget()
            self.button_forward.pack_forget()
            self.button_back = ttk.Button(
                self.control,
                command=self._back,
                text="  <  ")
            self.button_forward = ttk.Button(
                self.control,
                text="  >  ",
                state=tk.DISABLED)
            self.button_back.pack(padx=PADDING, pady=PADDING, side='left')
            self.button_forward.pack(padx=PADDING, pady=PADDING, side='left')

    def _back(self):
        self.canvas.delete('all')
        self.count -= 1
    
        self.canvas.create_image(CANVAS/2, CANVAS/2, image=self.image_list[self.count])

        if self.count < 2:
            self.button_back.pack_forget()
            self.button_forward.pack_forget()
            self.button_back = ttk.Button(
                self.control,
                command=self._back,
                text="  <  ")
            self.button_forward = ttk.Button(
                self.control,
                command=self._forward,
                text="  >  ")
            self.button_back.pack(padx=PADDING, pady=PADDING, side='left')
            self.button_forward.pack(padx=PADDING, pady=PADDING, side='left')
    
        if self.count == 0:
            self.button_back.pack_forget()
            self.button_forward.pack_forget()
            self.button_back = ttk.Button(
                self.control,
                text="  <  ",
                state=tk.DISABLED)
            self.button_forward = ttk.Button(
                self.control,
                command=self._forward,
                text="  >  ")
            self.button_back.pack(padx=PADDING, pady=PADDING, side='left')
            self.button_forward.pack(padx=PADDING, pady=PADDING, side='left')


class Shell(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.setup_widgets()

    def setup_widgets(self):
        pass


class Backend:
    def __init__(self) -> None:
        self._model = None
        self._path = None
        self._name = None

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def path(self) -> str:
        return self._path
    
    @property
    def info(self) -> str:
        return self._model[["faces.age", "quality"]].describe()

    @property
    def meta(self) -> str:
        return self._model["metadata"]
    
    @property
    def model(self) -> str:
        return self._model

    @name.setter
    def name(self, name) -> None:
        self._name = name
    
    @path.setter
    def path(self, path) -> None:
        self._path = path

    def load(self) -> None:
        if os.path.exists(self.path):
            with open(self.path) as f:
                data = json.load(f)
            self._model = pd.json_normalize(data)

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
    
    def run(self, **flag) -> None:
        pass
    
    def load(self) -> None:
        """Load existing results."""

        try:
            self.model.load()
        except Exception as error:
            self.view.show_message(error)
    
    def update(self) -> None:
        if self.view.file:
            self.model.path = self.view.file
    
    def save(self, file) -> None:
        """Save results."""

        try:
            msg = self.model.save(file)
            self.view.show_message(msg)
        except Exception as error:
            self.view.show_message(error)
    
    def restructure(self, model):
        pass

    def get_image(self, uid):
        pass

    def read_info(self):
        self.model.load()
        print(self.model.info)
        return self.model.info

    def get_boxplot(self):
        fig = plt.figure()

        # Draw a nested boxplot to show bills by day and time
        sns.boxplot(x="day", y="total_bill",
                    hue="smoker", palette=["m", "g"],
                    data=self.model)
        sns.despine(offset=10, trim=True)
        
        return fig
    
    def get_hist(self, attr):
        self.model.load()
        fig, ax = plt.subplots()

        sns.histplot(
            self.model.model,
            x="quality",
            hue=attr,
            multiple="stack"
        )

        return fig