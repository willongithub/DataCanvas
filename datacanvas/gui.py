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
        self.tk.call("set_theme", "dark")
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
        self.controller = Controller(self.model, self.view)


class Page(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

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
        self._setup_widgets()

    def _setup_widgets(self):
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

        # # self.canvas = tk.Canvas()

        # Tabs
        self.overview_tab = Tab(self, "overview")
        self.selector_tab = Tab(self, "selector")
        
        self.notebook.add(self.overview_tab, text="Overview")
        self.notebook.add(self.selector_tab, text="Selector")


class Tab(ttk.Frame):
    def __init__(self, parent, content):
        super().__init__(parent)
        
        # Create widget
        self._setup_widgets(content)

    def _setup_widgets(self, content):      
        self.sidebar = Sidebar(self)
        self.sidebar.pack(side='left')

        # Child widget
        if content == "overview":
            self.mainframe = Canvas(self)
            self.mainframe.pack(side='left')
        if content == "selector":
            self.mainframe = Selector(self)
            self.mainframe.pack(side='left')


class Sidebar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.filter_options = {
            'side': 'top',
            'padx': PADDING, 'pady': PADDING}
        
        self.field_options = ('1', '3', '5', '7')

        self.field_var = tk.StringVar(value=self.field_options[1])

        self._setup_widgets()

    def _setup_widgets(self):
        self.filter = ttk.LabelFrame(
            self,
            text='OPTIONS',
        )
        self.filter.pack(**self.filter_options)

        Options(self.filter, 'opt 1', self.field_options, self.field_var).pack()
        Options(self.filter, 'opt 2', self.field_options, self.field_var).pack()
        Options(self.filter, 'opt 3', self.field_options, self.field_var).pack()
        Options(self.filter, 'opt 4', self.field_options, self.field_var).pack()
        Options(self.filter, 'opt 5', self.field_options, self.field_var).pack()
        Options(self.filter, 'opt 6', self.field_options, self.field_var).pack()

        ttk.Button(
            self,
            text='Exit',
            command=self._exit
        ).pack(padx=PADDING, pady=PADDING, side='bottom')
        ttk.Button(
            self,
            text='Clear',
            command=self._clear_shell
        ).pack(padx=PADDING, pady=PADDING, side='bottom')
        ttk.Button(
            self,
            text='Theme',
            command=self._change_theme
        ).pack(padx=PADDING, pady=PADDING, side='bottom')

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


class Options(ttk.Frame):
    def __init__(self, parent, name, options, var):
        super().__init__(parent)

        self._setup_widgets(name, options, var)

    def _setup_widgets(self, name, options, var):
        self.field = ttk.LabelFrame(
            self,
            text=name,
        )
        self.field.pack(padx=PADDING, pady=PADDING)
        ttk.OptionMenu(
            self.field,
            var,
            options[0],
            *options,
        ).pack()


class Canvas(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self._setup_widgets()

    def _setup_widgets(self):
        self.plots = ttk.Notebook(
            self,
            width=WIDTH-SHELL,
            height=HEIGHT
        )
        self.plots.pack(padx=PADDING, pady=PADDING, side='left')
        self.fig_1 = ttk.Frame(
            self.plots,
            width=WIDTH-SHELL,
            height=HEIGHT
        )
        self.fig_1.pack(side='left', fill='y')
        self.plots.add(self.fig_1, text='fig 1')
        self.fig_2 = ttk.Frame(
            self.plots,
            width=WIDTH-SHELL,
            height=HEIGHT
        )
        self.fig_2.pack(side='left', fill='y')
        self.plots.add(self.fig_2, text='fig 2')


class Selector(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.image_list = [
            ImageTk.PhotoImage(Image.open("assets/image/img_1.jpg")),
            ImageTk.PhotoImage(Image.open("assets/image/img_2.jpg")),
            ImageTk.PhotoImage(Image.open("assets/image/img_3.jpg"))
        ]

        self.count = 0

        self._setup_widgets()

    def _setup_widgets(self):
        self.image = ttk.Frame(self)
        self.image.pack()
        self.label = ttk.Label(self.image, image=self.image_list[self.count])
        self.label.pack(side='top')
        
        self.button_back = ttk.Button(
            self,
            # command=self._back,
            state=tk.DISABLED,
            text="  <  ")
        
        self.button_forward = ttk.Button(
            self,
            command=self._forward,
            text="  >  ")
        
        # self.button_delete = ttk.Button(
        #     self,
        #     # command=self._delete,
        #     text="  x  ")
        
        self.button_back.pack(padx=PADDING, pady=PADDING, side='left')
        self.button_forward.pack(padx=PADDING, pady=PADDING, side='left')
        # self.button_delete.pack(padx=PADDING, pady=PADDING, side='left')
    
    def _forward(self):
        self.label.pack_forget()
        self.count += 1
    
        self.label = ttk.Label(self.image, image=self.image_list[self.count])
        self.label.pack(side='top')

        if self.count > 0:
            self.button_back.pack_forget()
            self.button_forward.pack_forget()
            self.button_back = ttk.Button(
                self,
                command=self._back,
                text="  <  ")
            self.button_forward = ttk.Button(
                self,
                command=self._forward,
                text="  >  ")
            self.button_back.pack(padx=PADDING, pady=PADDING, side='left')
            self.button_forward.pack(padx=PADDING, pady=PADDING, side='left')

        if self.count == 2:
            self.button_back.pack_forget()
            self.button_forward.pack_forget()
            self.button_back = ttk.Button(
                self,
                command=self._back,
                text="  <  ")
            self.button_forward = ttk.Button(self, text="  >  ",
                                    state=tk.DISABLED)
            self.button_back.pack(padx=PADDING, pady=PADDING, side='left')
            self.button_forward.pack(padx=PADDING, pady=PADDING, side='left')

    def _back(self):
        self.label.pack_forget()
        self.count -= 1
    
        self.label = ttk.Label(self.image, image=self.image_list[self.count])
        self.label.pack(side='top')

        if self.count < 2:
            self.button_back.pack_forget()
            self.button_forward.pack_forget()
            self.button_back = ttk.Button(
                self,
                command=self._back,
                text="  <  ")
            self.button_forward = ttk.Button(
                self,
                command=self._forward,
                text="  >  ")
            self.button_back.pack(padx=PADDING, pady=PADDING, side='left')
            self.button_forward.pack(padx=PADDING, pady=PADDING, side='left')
    
        if self.count == 0:
            self.button_back.pack_forget()
            self.button_forward.pack_forget()
            self.button_back = ttk.Button(self, text="  <  ",
                                    state=tk.DISABLED)
            self.button_forward = ttk.Button(
                self,
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
        pass

    @property
    def name(self) -> str:
        return self.name
    
    @property
    def path(self) -> str:
        return self.path

    @property
    def meta(self) -> str:
        return self.model["metadata"]

    @name.setter
    def name(self, name) -> str:
        self.name = name
    
    @path.setter
    def path(self, path) -> str:
        self.path = path

    def load(self, path) -> None:
        self.model = util.load(path)

    def run(self, **flag) -> None:
        self.model = util.run(flag)

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
    
    def save(self, file) -> None:
        """Save results."""

        try:
            msg = self.model.save(file)
            self.view.show_message(msg)
        except Exception as error:
            self.view.show_message(error)
    
    def restructure(self, model):
        pass

    def image(self, uid):
        pass
