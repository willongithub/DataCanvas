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
        
        # platformD = system()
        # if platformD == 'Darwin':
        #     icon = 'datacanvas/datacanvas.icns'
        # elif platformD == 'Windows':
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
        self.setup_widgets()

    def setup_widgets(self):
        self.app = Page(self)
        self.app.pack(fill="both", expand=True)


class Page(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        # # Make the app responsive
        # for index in [0, 1, 2]:
        #     self.columnconfigure(index=index, weight=1)
        #     self.rowconfigure(index=index, weight=1)

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

        # self.canvas = tk.Canvas()

        # Tabs
        self.overview_tab = Tab(self.notebook, "overview")
        self.selector_tab = Tab(self.notebook, "selector")
        
        self.notebook.add(self.overview_tab, text="Overview Tab")
        self.notebook.add(self.selector_tab, text="Selector Tab")


class Tab(ttk.Frame):
    def __init__(self, parent, child):
        ttk.Frame.__init__(self)
        
        # Create widget
        self.setup_widgets(child)

    def setup_widgets(self, child):
        self.tab = ttk.Frame(
            self,
            width=WIDTH-SHELL,
            height=HEIGHT)
        self.tab.pack(fill='both', expand=True)
        
        self.sidebar = Sidebar(self.tab)

        # Child widget
        if child == "overview":
            self.child = Canvas(self.tab)
        if child == "selector":
            self.child = Selector(self.tab)


class Shell(ttk.Frame):
    def __init__(self, parent):
        super().__init__(self)

        self.setup_widgets()

    def setup_widgets(self):
        pass


class Sidebar(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        self.sidebar_options = {
            'side': 'left', 'fill': 'both',
            'padx': PADDING, 'pady': PADDING}
        
        self.field_options = ('1', '3', '5', '7')

        self.field_option = tk.StringVar(value=self.field_options[1])

        self.setup_widgets(parent)

    def setup_widgets(self, parent):
        self.sidebar = ttk.LabelFrame(
            parent,
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

        ttk.Button(
            parent,
            text='Exit',
            command=self._exit
        ).pack(padx=PADDING, pady=PADDING, side='bottom')
        # ttk.Button(
        #     parent,
        #     text='Clear',
        #     command=lambda: self._clear_shell
        # ).pack(padx=PADDING, pady=PADDING, side='bottom')
        ttk.Button(
            parent,
            text='Theme',
            command=lambda: self._change_theme
        ).pack(padx=PADDING, pady=PADDING, side='bottom')

    # def _clear_shell(self):
    #     answer = askokcancel(
    #         title='Confirmation',
    #         message='CLI outout will be removed.',
    #         icon=WARNING
    #     )
    #     if answer:
    #         self.shell.delete('1.0', tk.END)
    #         showinfo(
    #             title='Status',
    #             message='CLI output all clear.'
    #         )
    
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


class Options(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        self.setup_widgets()

    def setup_widgets(self):
        self.sidebar = ttk.LabelFrame(
            self,
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


class Canvas(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        self.setup_widgets(parent)

    def setup_widgets(self, parent):
        self.plots = ttk.Notebook(
            parent,
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


class Selector(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        self.image_no_1 = ImageTk.PhotoImage(Image.open("assets/image/img_1.jpg"))
        self.image_no_2 = ImageTk.PhotoImage(Image.open("assets/image/img_2.jpg"))
        self.image_no_3 = ImageTk.PhotoImage(Image.open("assets/image/img_3.jpg"))
        
        # List of the images so that we traverse the list
        self.image_list = [self.image_no_1, self.image_no_2, self.image_no_3]

        self.setup_widgets(parent)

    def setup_widgets(self, parent):
        self.label = ttk.Label(image=self.image_no_1)
        
        # We have to show the the box so this below line is needed
        # self.label.grid(row=1, column=0, columnspan=3)
        self.label.pack()
        
        # We will have three button back ,forward and exit
        self.button_back = ttk.Button(
            parent,
            text="Back",
            command=self._back,
            state=tk.DISABLED)
        
        self.button_forward = ttk.Button(
            parent,
            text="Forward",
            command=lambda: self._forward(1))
        
        # grid function is for placing the buttons in the frame
        # self.button_back.grid(row=5, column=0)
        # self.button_forward.grid(row=5, column=2)
        self.button_back.pack()
        self.button_forward.pack()
        
    
    def _forward(self, img_no):
        self.label.grid_forget()
    
        # This is for clearing the screen so that
        # our next image can pop up
        self.label = ttk.Label(image=self.image_list[img_no-1])
    
        # as the list starts from 0 so we are
        # subtracting one
        # self.label.grid(row=1, column=0, columnspan=3)
        self.label.pack()

        self.button_for = ttk.Button(self, text="forward",
                            command=lambda: self._forward(img_no+1))
    
        # img_no+1 as we want the next image to pop up
        if img_no == 4:
            self.button_forward = ttk.Button(self, text="Forward",
                                    state=tk.DISABLED)
    
        # img_no-1 as we want previous image when we click
        # back button
        self.button_back = ttk.Button(self, text="Back",
                            command=lambda: self._back(img_no-1))
    
        # Placing the button in new grid
        # self.button_back.grid(row=5, column=0)
        # self.button_exit.grid(row=5, column=1)
        # self.button_for.grid(row=5, column=2)
        self.button_back.pack()
        self.button_exit.pack()
        self.button_forward.pack()

    def _back(self, img_no):
        self.label.grid_forget()
    
        # for clearing the image for new image to pop up
        self.label = ttk.Label(image=self.image_list[img_no - 1])
        self.label.grid(row=1, column=0, columnspan=3)
        self.button_forward = ttk.Button(self, text="forward",
                                command=lambda: self.forward(img_no + 1))
        self.button_back = ttk.Button(self, text="Back",
                            command=lambda: self.back(img_no - 1))
        print(img_no)
    
        # whenever the first image will be there we will
        # have the back button disabled
        if img_no == 1:
            self.button_back = ttk.Button(self, Text="Back", state=tk.DISABLED)
    
        # self.label.grid(row=1, column=0, columnspan=3)
        # self.button_back.grid(row=5, column=0)
        # self.button_exit.grid(row=5, column=1)
        # self.button_for.grid(row=5, column=2)
        self.label.grid()
        self.button_back.pack()
        self.button_exit.pack()
        self.button_forward.pack()