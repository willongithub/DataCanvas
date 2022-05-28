# !/usr/bin/env python3

"""General Tkinter GUI."""

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import WARNING, askokcancel, showinfo
from tkinter.scrolledtext import ScrolledText

import datacanvas.utils as util

WIDTH = 1280
HEIGHT = 800
SIDEBAR = 200
SHELL = 600
PADDING = 10


class DataCanvas(tk.Tk):
    """GUI class."""

    def __init__(self):
        super().__init__()

        self.title('DataCanvas')
        self.resizable(True, True)
        self.iconbitmap('datacanvas/datacanvas.ico')

        # Set theme
        self.tk.call("source", "assets/theme/sun-valley.tcl")
        self.tk.call("set_theme", "light")
        # style = ttk.Style(self)
        # style.theme_use('clam')

        self.field_1_option = tk.StringVar(self)
        self.field_1_options = ('1', '3', '5', '7')
        self.field_2_option = tk.StringVar(self)
        self.field_2_options = ('0.5', '0.6', '0.7', '0.8', '0.9')

        self.detection_mask = tk.BooleanVar(self)
        self.face_gender = tk.BooleanVar(self)
        self.face_ethnicity = tk.BooleanVar(self)
        self.face_emotion = tk.BooleanVar(self)
        self.face_age = tk.BooleanVar(self)
        self.image_quality = tk.DoubleVar(self)
        self.confidance_level = tk.DoubleVar(self)

        self.image_quality_options = ('1', '3', '5', '7')
        self.confidance_level = ('0.5', '0.6', '0.7', '0.8', '0.9')

        # Calculates location of screen centre to put the gui window.
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - WIDTH/2)
        center_y = int(screen_height/2 - HEIGHT/2)
        self.geometry(f'{WIDTH}x{HEIGHT}+{center_x}+{center_y}')

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(padx=PADDING, pady=PADDING, side='left')

        self.shell = ScrolledText(
            self,
            bg='gray20',
            fg='lime green',
            height=HEIGHT
        )
        self.shell.pack(side='left')

        self.canvas = tk.Canvas()

        sidebar_options = {
            'side': 'left', 'fill': 'both',
            'padx': PADDING, 'pady': PADDING}

        # Tab 1
        self.tab_1 = ttk.Frame(
            self.notebook,
            width=WIDTH-SHELL,
            height=HEIGHT)
        self.tab_1.pack(fill='both', expand=True)
        self.notebook.add(self.tab_1, text='Tab 1')
        
        self.sidebar_1 = ttk.LabelFrame(
            self.tab_1,
            text='OPTIONS',
        )
        self.sidebar_1.pack(**sidebar_options)
        
        self.field_1 = ttk.LabelFrame(
            self.sidebar_1,
            text='Field 1:',
        )
        self.field_1.pack(padx=PADDING, pady=PADDING)
        ttk.OptionMenu(
            self.field_1,
            self.field_1_option,
            self.field_1_options[0],
            *self.field_1_options,
        ).pack()

        # Plotting area.
        self.plots_1 = ttk.Notebook(
            self.tab_1,
            width=WIDTH-SHELL,
            height=HEIGHT
        )
        self.plots_1.pack(padx=PADDING, pady=PADDING, side='left')
        self.tab_1_1 = ttk.Frame(
            self.plots_1,
            width=WIDTH-SHELL,
            height=HEIGHT
        )
        self.tab_1_1.pack(side='left', fill='y')
        self.plots_1.add(self.tab_1_1, text='tab_1_1')
        self.tab_1_2 = ttk.Frame(
            self.plots_1,
            width=WIDTH-SHELL,
            height=HEIGHT
        )
        self.tab_1_2.pack(side='left', fill='y')
        self.plots_1.add(self.tab_1_2, text='tab_1_2')

        # Run and Exit buttons (Tab 1).
        ttk.Button(
            self.sidebar_1,
            text='Exit',
            command=self._exit
        ).pack(padx=PADDING, pady=PADDING, side='bottom')
        ttk.Button(
            self.sidebar_1,
            text='Clear',
            command=lambda: self._clear_shell()
        ).pack(padx=PADDING, pady=PADDING, side='bottom')
        ttk.Button(
            self.sidebar_1,
            text='Theme',
            command=lambda: self._change_theme()
        ).pack(padx=PADDING, pady=PADDING, side='bottom')


        # Tab 2
        self.tab_2 = ttk.Frame(
            self.notebook,
            width=WIDTH-SHELL,
            height=HEIGHT)
        self.tab_2.pack(fill='both', expand=True)
        self.notebook.add(self.tab_2, text='Tab 2')
        
        self.sidebar_2 = ttk.LabelFrame(
            self.tab_2,
            text='OPTIONS',
        )
        self.sidebar_2.pack(**sidebar_options)
        
        self.field_2 = ttk.LabelFrame(
            self.sidebar_2,
            text='Field 2:',
        )
        self.field_2.pack(padx=PADDING, pady=PADDING)
        ttk.OptionMenu(
            self.field_2,
            self.field_2_option,
            self.field_2_options[0],
            *self.field_2_options,
        ).pack()

        # Plotting area.
        self.plots_2 = ttk.Notebook(
            self.tab_2,
            width=WIDTH-SHELL,
            height=HEIGHT
        )
        self.plots_2.pack(padx=PADDING, pady=PADDING, side='left')
        self.tab_2_1 = ttk.Frame(
            self.plots_2,
            width=WIDTH-SHELL,
            height=HEIGHT
        )
        self.tab_2_1.pack(side='left', fill='y')
        self.plots_2.add(self.tab_2_1, text='tab_2_1')
        self.tab_2_2 = ttk.Frame(
            self.plots_2,
            width=WIDTH-SHELL,
            height=HEIGHT
        )
        self.tab_2_2.pack(side='left', fill='y')
        self.plots_2.add(self.tab_2_2, text='tab_2_2')

        # Run and Exit buttons (Tab 2).
        ttk.Button(
            self.sidebar_2,
            text='Exit',
            command=self._exit
        ).pack(padx=PADDING, pady=PADDING, side='bottom')
        ttk.Button(
            self.sidebar_2,
            text='Clear',
            command=lambda: self._clear_shell()
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
