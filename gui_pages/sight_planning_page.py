import os
import tkinter as tk
import ttkbootstrap as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import utilities.celestial_engine as celestial_engine
from utilities.sight_planning import SightSessionPlanning
from gui_pages.sight_entry_page import SightEntryPage
from utilities.autocompletion import AutoComplete
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.tooltip import ToolTip
from utilities.tooltips import TextExtractor

class SightPlanningPage(ttk.Frame):
    def __init__(self, container, PageOne):
        super().__init__(container)
        self.gui_page1 = PageOne

        self.create_label_frames()
        self.create_notebook()
        self.create_planning_controls_page()
        self.create_time_of_phenomena_treeview()
        self.create_planning_treeview()
        self.create_optimal_triad_treeview()
        self.autocompletion_binding()
        self.create_tooltips()

         # Configure the weights for the SightPlanningPage frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

      
        
    def create_label_frames(self):
        self.sight_planning_frame = ttk.LabelFrame(self, text='Sight Planning')

        # grid, fill both directions
        self.sight_planning_frame.grid(row=0, column=0, sticky='NESW')

        # Configure the weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


    def create_notebook(self):
        self.notebook = ttk.Notebook(self.sight_planning_frame)
        
        # grid
        self.notebook.grid(row=0, column=0, sticky='NESW')

        # Configure the weights
        self.sight_planning_frame.grid_rowconfigure(0, weight=1)
        self.sight_planning_frame.grid_columnconfigure(0, weight=1)


        self.page1 = ttk.Frame(self.notebook)
        self.page1.grid(sticky='nsew')  # Use grid instead of pack
        self.page1.grid_rowconfigure(0, weight=1)
        self.page1.grid_columnconfigure(0, weight=1)

        self.page2 = ttk.Frame(self.notebook)
        self.page2.grid(sticky='nsew')  # Use grid instead of pack
        self.page2.grid_rowconfigure(0, weight=1)
        self.page2.grid_columnconfigure(0, weight=1)

        self.page3 = ttk.Frame(self.notebook)
        self.page3.grid(sticky='nsew')  # Use grid instead of pack
        self.page3.grid_rowconfigure(0, weight=1)
        self.page3.grid_columnconfigure(0, weight=1)

        self.page4 = ttk.Frame(self.notebook)
        self.page4.grid(sticky='nsew')  # Use grid instead of pack
        self.page4.grid_rowconfigure(0, weight=1)
        self.page4.grid_columnconfigure(0, weight=1)

        self.notebook.add(self.page1, text='Planning Control')
        self.notebook.add(self.page3, text='Visible Bodies')
        self.notebook.add(self.page4, text='Optimal Triads')

        self.page1.master = self
        self.page2.master = self
        self.page3.master = self
        self.page4.master = self


    def create_planning_controls_page(self):
        # create label frames
        self.planning_controls_frame = ttk.LabelFrame(self.page1, text='Planning Controls')
        
        # grid
        self.planning_controls_frame.grid(row=0, column=0)

        self.phenoma_frame = ttk.LabelFrame(self.page1, text='Phenomena')
        
        # grid
        self.phenoma_frame.grid(row=1, column=0, sticky='NESW')

        # create label and entry fields for date, time, dr latitude, dr longitude
        # Date
        self.date_label = ttk.Label(self.planning_controls_frame, text='Date')
        self.date_label.grid(row=0, column=0, padx=10, pady=10, sticky='W')
        self.date_entry = ttk.Entry(self.planning_controls_frame, width = 12)
        self.date_entry.grid(row=0, column=1, padx=10, pady=10, sticky='W')

  
        # Time
        self.time_label = ttk.Label(self.planning_controls_frame, text='Time')
        self.time_label.grid(row=1, column=0, padx=10, pady=10, sticky='W')
        self.time_entry = ttk.Entry(self.planning_controls_frame, width = 12)
        self.time_entry.grid(row=1, column=1, padx=10, pady=10, sticky='W')

  
        # labels and Inputs for DR Latitude, Longitude
  
        # DR Latitude
        self.dr_latitude_label = ttk.Label(self.planning_controls_frame, text='DR Latitude')
        self.dr_latitude_label.grid(row=2, column=0, padx=10, pady=10, sticky='W')

        self.dr_latitude_entry = ttk.Entry(self.planning_controls_frame, width = 12)
        self.dr_latitude_entry.grid(row=2, column=1, padx=10, pady=10, sticky='W')

  
        # DR Longitude
        self.dr_longitude_label = ttk.Label(self.planning_controls_frame, text='DR Longitude')
        self.dr_longitude_label.grid(row=3, column=0, padx=10, pady=10, sticky='W')

  
        self.dr_longitude_entry = ttk.Entry(self.planning_controls_frame, width = 12)
        self.dr_longitude_entry.grid(row=3, column=1, padx=10, pady=10, sticky='W')

        # make entry fields helvetica, 12, bold
        self.dr_latitude_entry.configure(font=('Helvetica', 12, 'bold'))
        self.dr_longitude_entry.configure(font=('Helvetica', 12, 'bold'))
        self.date_entry.configure(font=('Helvetica', 12, 'bold'))
        self.time_entry.configure(font=('Helvetica', 12, 'bold'))

        # make labels helvetica, 12, bold
        self.dr_latitude_label.configure(font=('Helvetica', 12, 'bold'))
        self.dr_longitude_label.configure(font=('Helvetica', 12, 'bold'))
        self.date_label.configure(font=('Helvetica', 12, 'bold'))
        self.time_label.configure(font=('Helvetica', 12, 'bold'))

    
        # create buttons

        # make button text "Select a Time of Phenomena", and then when clicked, change text to "Plan For Selected Time"

        
        self.set_planning_time_button = ttk.Button(self.planning_controls_frame, text = 'Select a Time of Phenomena',
                                                        style='primary.Outline.TButton',
                                                       command= lambda: SightSessionPlanning(self.gui_page1.dr_entry_fields,
                                                                                             [self.time_of_phenomena_treeview,
                                                                                              self.planning_treeview,
                                                                                              self.optimal_triad_treeview
                                                                                              ],
                                                                                              [self.date_entry,
                                                                                               self.time_entry,
                                                                                               self.dr_latitude_entry,
                                                                                               self.dr_longitude_entry,
                                                                                               ]))
        
        # self.set_planning_time_button = ttk.Button(self.planning_controls_frame, text = 'Plan',
        #                                                 style='primary.Outline.TButton',
        #                                                command= lambda: SightSessionPlanning(self.gui_page1.dr_entry_fields,
        #                                                                                      [self.time_of_phenomena_treeview,
        #                                                                                       self.planning_treeview,
        #                                                                                       self.optimal_triad_treeview
        #                                                                                       ],
        #                                                                                       [self.date_entry,
        #                                                                                        self.time_entry,
        #                                                                                        self.dr_latitude_entry,
        #                                                                                        self.dr_longitude_entry,
        #                                                                                        ]))

        
        self.set_planning_time_button.grid(row=4, column=0, padx=10, pady=10, sticky='W', columnspan=7)


    def check(self):
        # if self.gui_page1.entry_fields are all complete, then instantiate SightSessionPlanning

        if all([entry.get() for entry in self.gui_page1.entry_fields[:5]]):
            # Instantiate SightSessionPlanning
            SightSessionPlanning(self.gui_page1.entry_fields,
                                 [self.time_of_phenomena_treeview,
                                  self.planning_treeview,
                                  self.optimal_triad_treeview],
                                 [self.date_entry,
                                  self.time_entry,
                                  self.dr_latitude_entry,
                                  self.dr_longitude_entry])
        else:
            Messagebox.show_error('Error', 'Please complete all fields')

    def create_time_of_phenomena_treeview(self):
        # add treeview to page 2
        self.time_of_phenomena_treeview = ttk.Treeview(self.phenoma_frame, style = 'danger.Treeview')
        
        # grid
        self.time_of_phenomena_treeview.grid(row=0, column=0, padx=10, pady=10, sticky='NESW')

        # Configure the weights
        self.phenoma_frame.grid_rowconfigure(0, weight=1)
        self.phenoma_frame.grid_columnconfigure(0, weight=1)

        
        # add date, time, event columns
        self.time_of_phenomena_treeview['columns'] = ('Date GMT', 'Date LMT', 'Event')


        # format columns
        self.time_of_phenomena_treeview.column('#0', width=0, stretch='no')
        self.time_of_phenomena_treeview.column('Date GMT', anchor='center', width=100)
        self.time_of_phenomena_treeview.column('Date LMT', anchor='center', width=100)
        self.time_of_phenomena_treeview.column('Event', anchor='center', width=100)

        # add headings
        self.time_of_phenomena_treeview.heading('#0', text='', anchor='w')
        self.time_of_phenomena_treeview.heading('Date GMT', text='Date GMT', anchor='center')
        self.time_of_phenomena_treeview.heading('Date LMT', text='Date LMT', anchor='center')
        self.time_of_phenomena_treeview.heading('Event', text='Event', anchor='center')

        # if the user selects row by clicking or scrolling, call the auto_fill_data_time function

        self.time_of_phenomena_treeview.bind('<ButtonRelease-1>', lambda event: self.auto_fill_date_time_entries())
        self.time_of_phenomena_treeview.bind('<KeyRelease>', lambda event: self.auto_fill_date_time_entries())

    def create_planning_treeview(self):
        # add treeview to page 3 
        self.planning_treeview = ttk.Treeview(self.page3)
        
        # grid
        self.planning_treeview.grid(row=0, column=0, padx=10, pady=10, sticky='NESW')

        # add body, altitude, and azimuth columns
        self.planning_treeview['columns'] = ('Body', 'Altitude', 'Azimuth', 'Magnitude')

        # format columns
        self.planning_treeview.column('#0', width=0, stretch='no')
        self.planning_treeview.column('Body', anchor='center', width=100)
        self.planning_treeview.column('Altitude', anchor='center', width=100)
        self.planning_treeview.column('Azimuth', anchor='center', width=100)
        self.planning_treeview.column('Magnitude', anchor='center', width=100)

        # add headings
        self.planning_treeview.heading('#0', text='', anchor='w')
        self.planning_treeview.heading('Body', text='Body', anchor='center')
        self.planning_treeview.heading('Altitude', text='Altitude', anchor='center')
        self.planning_treeview.heading('Azimuth', text='Azimuth', anchor='center')
        self.planning_treeview.heading('Magnitude', text='Magnitude', anchor='center')


    def create_optimal_triad_treeview(self):
        # add treeview to page 4
        self.optimal_triad_treeview = ttk.Treeview(self.page4)
        
        # grid
        self.optimal_triad_treeview.grid(row=0, column=0, padx=10, pady=10, sticky='NESW')

        # add body, altitude, azimuth, and magnitude columns
        self.optimal_triad_treeview['columns'] = ('Body', 'Altitude', 'Azimuth', 'Magnitude')

        # format columns
        self.optimal_triad_treeview.column('#0', width=0, stretch='no')
        self.optimal_triad_treeview.column('Body', anchor='center', width=100)
        self.optimal_triad_treeview.column('Altitude', anchor='center', width=100)
        self.optimal_triad_treeview.column('Azimuth', anchor='center', width=100)
        self.optimal_triad_treeview.column('Magnitude', anchor='center', width=100)

        # add headings
        self.optimal_triad_treeview.heading('#0', text='', anchor='w')
        self.optimal_triad_treeview.heading('Body', text='Body', anchor='center')
        self.optimal_triad_treeview.heading('Altitude', text='Altitude', anchor='center')
        self.optimal_triad_treeview.heading('Azimuth', text='Azimuth', anchor='center')
        self.optimal_triad_treeview.heading('Magnitude', text='Magnitude', anchor='center')

       

    def auto_fill_date_time_entries(self):
        # get date and time from sight planning treeview and fill in date and time entries

        # get selected item from treeview
        selected_item = self.time_of_phenomena_treeview.focus()

        # get values from selected item
        values = self.time_of_phenomena_treeview.item(selected_item, 'values')

        # fill in date and time entries with selected values
        self.date_entry.delete(0, 'end')
        
        # parse date and time from value
        date = values[0].split(' ')[0]

        # fill in date entry
        self.date_entry.insert(0, date)

        # fill in time entry
        self.time_entry.delete(0, 'end')
        self.time_entry.insert(0, values[0].split(' ')[1])

        # after filling time entry, if it is missing values in the seconds, add :00, else leave it alone
        if len(self.time_entry.get()) < 8:
            self.time_entry.insert(6, ':00')
        
        return 
    
    def autocompletion_binding(self):
        # initialize autocompletion
        self.autocomplete = AutoComplete(self.master)

        # bind autocompletion to date and time entries
        self.date_entry.bind('<KeyRelease>', lambda event: self.autocomplete.date_formatting(event, self.date_entry))
        self.time_entry.bind('<KeyRelease>', lambda event: self.autocomplete.time_formatting(event, self.time_entry))

    def create_tooltips(self):

        # Get the directory where the current script (presumably __main__.py or similar) is located
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # go up one directory from current_dir
        script_dir = os.path.dirname(current_dir)
        
        # Construct the absolute path to tooltips.txt
        tooltips_path = os.path.join(script_dir, 'text_files', 'tooltips.txt')

        self.extractor = TextExtractor(tooltips_path) 

        # tooltip for notebook page 1
        page1_tooltip = self.extractor.get_text('sight_planning')
        ToolTip(self.page1, text=page1_tooltip)

        # tooltip for sight planning treeview
        planning_tooltip = self.extractor.get_text('visible_bodies')
        ToolTip(self.planning_treeview, text=planning_tooltip)

        # tooltip for optimal triad treeview
        optimal_tooltip = self.extractor.get_text('sorted_triads')
        ToolTip(self.optimal_triad_treeview, text=optimal_tooltip)

        # tooltip for button
        button_tooltip = self.extractor.get_text('sight_planning')
        ToolTip(self.planning_controls_frame, text=button_tooltip)

        # tooltip for time of phenomena treeview
        time_of_phenomena_tooltip = self.extractor.get_text('time_of_phenomena')
        ToolTip(self.time_of_phenomena_treeview, text=time_of_phenomena_tooltip)