# !/usr/bin/env python3

"""General Tkinter GUI."""

import tkinter as tk
from platform import system
from tkinter import ttk
from tkinter.messagebox import WARNING, askokcancel, showinfo
from tkinter.scrolledtext import ScrolledText

from PIL import Image, ImageTk

import datacanvas.utils as util

WIDTH = 1280
HEIGHT = 800
SIDEBAR = 200
SHELL = 600
PADDING = 10


class DataCanvas(tk.Tk):
    """GUI window class."""

    def __init__(self):
        super().__init__()

        self.title('DataCanvas')
        self.resizable(True, True)
        
        platformD = system()
        if platformD == 'Darwin':
            icon = 'datacanvas/datacanvas.icns'
        elif platformD == 'Windows':
            icon = 'datacanvas/datacanvas.ico'
        else:
            icon = 'datacanvas/datacanvas.xbm'
        self.iconbitmap(icon)

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

        self.app = Page(self)
        self.app.pack(fill="both", expand=True)


class Page(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        # Make the app responsive
        for index in [0, 1, 2]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        # Create option list
        self.image_quality_options = ['1', '3', '5', '7']
        self.confidance_level = ['0.5', '0.6', '0.7', '0.8', '0.9']

        # Create option variables
        self.detection_mask = tk.BooleanVar(value=True)
        self.face_gender = tk.BooleanVar(value=True)
        self.face_ethnicity = tk.BooleanVar(value=True)
        self.face_emotion = tk.BooleanVar(value=True)
        self.face_age = tk.BooleanVar(value=True)
        self.image_quality = tk.DoubleVar(value=self.image_quality_options[1])
        self.confidance_level = tk.DoubleVar(value=self.confidance_level[1])
    
        # Create widget
        self.setup_widgets()

    def setup_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(padx=PADDING, pady=PADDING, side='left')

        # Shell style output area
        self.shell = ScrolledText(
            self,
            bg='gray20',
            fg='lime green',
            height=HEIGHT
        )
        self.shell.pack(side='left')

        self.canvas = tk.Canvas()

        # Tab
        self.tab = Tab(self.notebook)
        self.notebook.add(self.tab, text="Tab New")

class Tab(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        self.sidebar_options = {
            'side': 'left', 'fill': 'both',
            'padx': PADDING, 'pady': PADDING}

        self.field_options = ('1', '3', '5', '7')

        self.field_option = tk.StringVar(value=self.field_options[1])
        
        # Create widget
        self.setup_widgets()

    def setup_widgets(self):
        self.tab = ttk.Frame(
            self,
            width=WIDTH-SHELL,
            height=HEIGHT)
        self.tab.pack(fill='both', expand=True)
        # self.add(self.tab, text='Tab 1')
        
        self.sidebar = ttk.LabelFrame(
            self.tab,
            text='OPTIONS',
        )
        self.sidebar.pack(**self.sidebar_options)
        
        self.field = ttk.LabelFrame(
            self.sidebar,
            text='Field 1:',
        )
        self.field.pack(padx=PADDING, pady=PADDING)
        ttk.OptionMenu(
            self.field,
            self.field_option,
            self.field_options[0],
            *self.field_options,
        ).pack()

        # Plotting area.
        self.plots = ttk.Notebook(
            self.tab,
            width=WIDTH-SHELL,
            height=HEIGHT
        )
        self.plots.pack(padx=PADDING, pady=PADDING, side='left')
        self.tab_1_1 = ttk.Frame(
            self.plots,
            width=WIDTH-SHELL,
            height=HEIGHT
        )
        self.tab_1_1.pack(side='left', fill='y')
        self.plots.add(self.tab_1_1, text='tab_1_1')
        self.tab_1_2 = ttk.Frame(
            self.plots,
            width=WIDTH-SHELL,
            height=HEIGHT
        )
        self.tab_1_2.pack(side='left', fill='y')
        self.plots.add(self.tab_1_2, text='tab_1_2')

        # Run and Exit buttons.
        ttk.Button(
            self.sidebar,
            text='Exit',
            command=self._exit
        ).pack(padx=PADDING, pady=PADDING, side='bottom')
        ttk.Button(
            self.sidebar,
            text='Clear',
            command=lambda: self._clear_shell()
        ).pack(padx=PADDING, pady=PADDING, side='bottom')
        ttk.Button(
            self.sidebar,
            text='Theme',
            command=lambda: self._change_theme()
        ).pack(padx=PADDING, pady=PADDING, side='bottom')

    # Local functions
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

class Option(ttk.Frame):
    pass

class Shell(ttk.Frame):
    pass

class Canvas(ttk.Frame):
    pass

class ImageSelector(ttk.Frame):
    pass