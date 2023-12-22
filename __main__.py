# Author: Alex Spradling
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.window import Window
from gui_pages import splash_page as splash_page
from gui_pages import sight_entry_page as sight_entry_page
from gui_pages import lop_plot_page as lop_plot_page
from gui_pages import fit_slope_page as fit_slope_page
from gui_pages import sight_planning_page as sight_planning_page
from gui_pages import azimuth_page as azimuth_page
from utilities.sight_handling import load_sights_from_clipboard, save_sights_to_clipboard, open_sight_log
from utilities.os_handler import get_os_type

"""
Capella is a celestial navigation program that allows the user to enter sights, plot lines of position, and perform sight reduction calculations. The goal is to provide a simple, intuitive interface for performing celestial navigation calculations that is also robust and uses modern mathematical methods for sight reduction evaluation.
"""


class CapellaApp(ttk.Frame):

    def create_notebook(self):
        # create pages
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky='NESW')
        self.splash_page = splash_page.SplashPage(self.notebook)
        self.page1 = sight_entry_page.SightEntryPage(self.notebook)
        self.page2 = lop_plot_page.LOPPlotPage(self.notebook)
        self.page3 = fit_slope_page.FitSlopePage(self.notebook)
        self.page4 = sight_planning_page.SightPlanningPage(self.notebook, self.page1)
        self.page5 = azimuth_page.AzimuthPage(self.notebook)


    def add_splash(self):
        # add splash page to notebook
        self.notebook.add(self.splash_page, text='Terms of Use')
        self.splash_page.button.config(command=self.add_pages_to_notebook)

    def add_pages_to_notebook(self):
        # destroy splash page
        self.splash_page.destroy()

        # add pages to notebook
        self.notebook.add(self.page1, text='DR/Sight Entry', padding=10)
        self.notebook.add(self.page2, text='LOP Plot', padding=10)
        self.notebook.add(self.page3, text='Fit Slope Analysis', padding=10)
        self.notebook.add(self.page4, text='Sight Planning', padding=10)
        self.notebook.add(self.page5, text='Azimuth', padding=10)

    def __init__(self, container):
       # create notebook
        super().__init__(container)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.create_menu()
        self.create_notebook()
        self.add_splash()

        # store pages as attributes of LandingPage Class
        self.page1.master = self
        self.page2.master = self
        self.page3.master = self
        self.page4.master = self

    def create_menu(self):
        # create menu
        self.menubar = tk.Menu(self)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label='Exit', command=self.quit, accelerator='Ctrl+q')

        # run sight_loader.py
        self.filemenu.add_command(
            label='Load Sights', command=lambda: load_sights_from_clipboard(
            self.page1,
            self.page1.fields,
            self.page1.sight_list_treeview
            ),
            accelerator='Ctrl+l'
        )
        self.filemenu.add_command(
            label='Save Sights', command=lambda: save_sights_to_clipboard(
            self.page1,
            self.page1.fields,
            self.page1.sight_list_treeview
            ),
            accelerator='Ctrl+s'
        )

        self.filemenu.add_command(
            label='Open Sight Log', command=lambda:open_sight_log(),
            accelerator='Ctrl+o'
        )

        self.menubar.add_cascade(label='File', menu=self.filemenu)
        self.master.config(menu=self.menubar)

        self.bind_all('<Control-q>', lambda e: self.quit())
        self.bind_all('<Control-l>', lambda e: load_sights_from_clipboard(
            self.page1,
            self.page1.fields,
            self.page1.sight_list_treeview
            )
        )
        self.bind_all('<Control-s>', lambda e: save_sights_to_clipboard(
            self.page1,
            self.page1.fields,
            self.page1.sight_list_treeview
            )
        )
        self.bind_all('<Control-o>', lambda e: open_sight_log())


if __name__ == '__main__':
    # if it is a unix OS:

    # determine if the OS is linux or mac
    if get_os_type() == 'Unix' or get_os_type() == 'Darwin':
        root = Window(title='Capella', themename='darkly', hdpi=False, scaling=1.35)
    # if it is a windows OS:
    elif get_os_type() == 'Windows':
        root = Window(title='Capella', themename='darkly')
    else:
        raise Exception('OS not recognized')


    # Configure the weights for the root window
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # create landing page
    landing_page = CapellaApp(root)

    # pack landing page
    landing_page.pack(expand=True, fill='both')

    # run mainloop
    root.mainloop()
