# !/usr/bin/env python3

"""General Tkinter GUI."""

import tkinter as tk
from platform import system
from tkinter import filedialog as fd
from tkinter import ttk
from tkinter.messagebox import WARNING, askokcancel, showinfo
from tkinter.scrolledtext import ScrolledText

from PIL import Image, ImageTk

import datacanvas.utils as util

WIDTH = 1280
HEIGHT = 800
SIDEBAR = 200
SHELL = 500
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

        # Setup View
        self.view = Page(self)
        self.view.pack(fill="both", expand=True)

        # Setup Controller
        self.controller = Controller(self.model, self.view)


class Page(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
    
        # Create widget
        self._setup_widgets()

    def _setup_widgets(self):
        Control(self).pack(side='bottom')
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


class Control(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self._setup_widgets()

    def _setup_widgets(self):
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
            command=self._get_results
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

    def _get_results(self):
        pass

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


class Plot(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self._setup_widgets()

    def _setup_widgets(self):
        self.plots = ttk.Notebook(
            self,
            width=WIDTH-SHELL,
            height=HEIGHT
        )
        self.plots.pack(pady=PADDING, side='left')
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
        
        # self.button_delete = ttk.Button(
        #     self,
        #     # command=self._delete,
        #     text="  x  ")
        
        self.button_back.pack(padx=PADDING, pady=PADDING, side='left')
        self.button_forward.pack(padx=PADDING, pady=PADDING, side='left')
        # self.button_delete.pack(padx=PADDING, pady=PADDING, side='left')
    
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
