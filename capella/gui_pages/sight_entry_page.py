


import tkinter as tk
import os
import ttkbootstrap as ttk
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.widgets import Floodgauge
from ttkwidgets.autocomplete import AutocompleteCombobox
import capella.utilities.celestial_engine as cnav
from capella.utilities.sight_handling import add_new_sight, delete_sight, update_sight, UpdateAndAveraging
from capella.utilities.reduce_sight import CapellaSightReduction
from capella.utilities.input_checking import InputChecking
from capella.utilities.autocompletion import AutoComplete
from capella.utilities.sight_planning import SightSessionPlanning
from capella.utilities.tooltips import TextExtractor

class SightEntryPage(ttk.Frame):
    
    # sight treeview class variable
    counter = 0
    def __init__(self, container):
        super().__init__(container)

        self.create_label_frames()
        self.create_notebook()
        self.create_sight_treeview()
        self.create_dr_info_entry()
        self.create_sextant_info_entry()
        self.create_sight_info_entry()
        self.create_fix_info_entry()
        self.aggregate_entry_fields()
        self.autocompletion_binding()
        self.create_tooltips()

        # binds 
        self.sight_list_treeview.bind('<<TreeviewSelect>>', 
                                      lambda event: UpdateAndAveraging(self.sight_list_treeview,
                                                                       self.sight_entry_fields).print_element(event))
        self.sight_list_treeview.bind('<<TreeviewSelect>>', lambda event: (
            self.notebook.select(self.notebook.tabs()[2]),
            UpdateAndAveraging(self.sight_list_treeview, self.sight_entry_fields).print_element(event)
        ))
        
  
    def create_label_frames(self):

        self.sight_frame = ttk.LabelFrame(self, text='Sight List')
        self.sight_frame.pack(expand = True, fill = "both")

    def create_notebook(self):

        # create label frame
        self.notebook_frame = ttk.LabelFrame(self, text = 'Session Menu')
        self.notebook_frame.pack(expand = True, fill = 'both')
        self.notebook = ttk.Notebook(self.notebook_frame)
        
        # grid
        self.notebook.pack(expand = True, fill = "both") 
                
        self.entry_page_1 = ttk.Frame(self.notebook)
        self.entry_page_1.pack(expand = False)
        self.dr_info_frame = self.entry_page_1

        self.entry_page_2 = ttk.Frame(self.notebook)
        self.entry_page_2.pack(expand = False )
        self.sextant_info_frame = self.entry_page_2

        self.entry_page_3 = ttk.Frame(self.notebook)
        self.entry_page_3.pack(expand = False)
        self.sight_info_entry_frame = self.entry_page_3

        self.entry_page_4 = ttk.Frame(self.notebook)
        self.entry_page_4.pack(expand = False)
        self.fix_info_frame = self.entry_page_4

        self.notebook.add(self.entry_page_1, text='DR Info.')
        self.notebook.add(self.entry_page_2, text='Sextant Info.')
        self.notebook.add(self.entry_page_3, text = 'Sight Entry')
        self.notebook.add(self.entry_page_4, text='Fix Computation')
       
    def create_sight_treeview(self):
        # Configure the style for the treeview
        style = ttk.Style()
        style.configure('info.Treeview', rowheight=50) 

        # create treeview
        self.sight_list_treeview = ttk.Treeview(self.sight_frame, height=10, style = 'info.Treeview')

        # With these lines:
        self.sight_frame.grid_rowconfigure(0, weight=1)
        self.sight_frame.grid_columnconfigure(0, weight=1)
        self.sight_list_treeview.grid(row=0, column=0, ipadx=10, ipady=10, sticky='nsew')
                
        # add columns to treeview
        self.sight_list_treeview['columns'] = ('Body', 'Hs', 'Date', 'Time')
        self.sight_list_treeview.column('#0', width=0, stretch='no')
        self.sight_list_treeview.column('Body', anchor='center', width=140)
        self.sight_list_treeview.column('Hs', anchor='center', width=140)
        self.sight_list_treeview.column('Date', anchor='center', width=140)
        self.sight_list_treeview.column('Time', anchor='center', width=140)
        
        # add headings to treeview
        self.sight_list_treeview.heading('#0', text='', anchor='w')
        self.sight_list_treeview.heading('Body', text='Body', anchor='center')
        self.sight_list_treeview.heading('Hs', text='Hs', anchor='center')
        self.sight_list_treeview.heading('Date', text='Date', anchor='center')
        self.sight_list_treeview.heading('Time', text='Time', anchor='center')

                       

    def create_dr_info_entry(self):
        """
        Creates label frame, entry field and labels for DR info and sextant info with 3 columns and 4 rows

        Args:
            self: instance of PageOne class
            DR Date
            DR Time
            DR Latitude
            DR Longitude
            Pressure
            Fix Date
            Fix Time
        """
        
        # create labels
        self.dr_date_label = ttk.Label(self.dr_info_frame, text='DR Date UTC:')
        self.dr_time_label = ttk.Label(self.dr_info_frame, text='DR Time UTC:')
        self.dr_latitude_label = ttk.Label(self.dr_info_frame, text='DR Latitude:')
        self.dr_longitude_label = ttk.Label(self.dr_info_frame, text='DR Longitude:')
        self.course_label = ttk.Label(self.dr_info_frame, text='Course:')
        self.speed_label = ttk.Label(self.dr_info_frame, text='Speed kts:')
        

        # configure labels

        self.dr_date_label.config(font=('Helvetica', 10, 'bold'), foreground='green')
        self.dr_time_label.config(font=('Helvetica', 10, 'bold'), foreground='green')
        self.dr_latitude_label.config(font=('Helvetica', 10, 'bold'), foreground='green')
        self.dr_longitude_label.config(font=('Helvetica', 10, 'bold'), foreground='green')
        self.course_label.config(font=('Helvetica', 10, 'bold'), foreground='green')
        self.speed_label.config(font=('Helvetica', 10, 'bold'), foreground='green')
                
        # create string variables
        self.dr_date = tk.StringVar(self)
        self.dr_time = tk.StringVar(self)
        self.dr_latitude = tk.StringVar(self)
        self.dr_longitude = tk.StringVar(self)
        self.course = tk.StringVar(self)
        self.speed = tk.StringVar(self)
        
        # create validation command instance 
        self.validate_number = self.register(InputChecking.validate_number)
        self.check_time_format = self.register(InputChecking.check_time_format)
        self.check_date_format = self.register(InputChecking.check_date_format)
        self.check_hs_format = self.register(InputChecking.check_hs_format)
        self.check_lat_format = self.register(InputChecking.check_lat_format)
        self.check_long_format = self.register(InputChecking.check_long_format)
        
        # create entries
        first_row_width = 12
        second_row_width = 12

        self.dr_date_entry = ttk.Entry(self.dr_info_frame, 
                                       textvariable=self.dr_date, 
                                       width=first_row_width,
                                       validate='focusout', 
                                       validatecommand=(self.check_date_format, '%P'),
                                       )
        
        self.dr_time_entry = ttk.Entry(self.dr_info_frame, 
                                       width=first_row_width,
                                       textvariable=self.dr_time, 
                                       validate='focusout',
                                       validatecommand=(self.check_time_format, '%P'))
        
        self.dr_latitude_entry = ttk.Entry(self.dr_info_frame, 
                                           width= first_row_width,
                                           textvariable=self.dr_latitude,
                                           validate='focusout',
                                           validatecommand=(self.check_lat_format, '%P'))
        
        self.dr_longitude_entry = ttk.Entry(self.dr_info_frame, 
                                            width=first_row_width,
                                            textvariable=self.dr_longitude,
                                            validate='focusout',
                                            validatecommand=(self.check_long_format, '%P'))
        
        self.course_entry = ttk.Entry(self.dr_info_frame, 
                                      textvariable=self.course, 
                                      width=second_row_width,
                                      validate='focusout',
                                      validatecommand=(self.validate_number, '%P'))
        
        self.speed_entry = ttk.Entry(self.dr_info_frame, 
                                     textvariable=self.speed, 
                                     width=second_row_width,
                                     validate='focusout',
                                     validatecommand=(self.validate_number, '%P'))



        self.dr_entry_fields = [self.dr_date_entry, 
                             self.dr_time_entry, 
                             self.dr_latitude_entry, 
                             self.dr_longitude_entry,
                             self.course_entry, 
                             self.speed_entry, 
                             ]
        
        self.dr_text_variables = [self.dr_date, 
                                  self.dr_time, 
                                  self.dr_latitude, 
                                  self.dr_longitude, 
                                  self.course, 
                                  self.speed, 
                                  ]
        
        # make the entry fields bold 
        for entry in self.dr_entry_fields:
            entry.config(font=('Helvetica', 12, 'bold'), justify='center')
        

        # Grid labels
        label_padx = 10
        label_pady = 10
        entry_padx = 10
        entry_pady = 10

        # Grid labels, put in center of label frame
        self.dr_date_label.grid(row=0, column=0, sticky='E', padx=label_padx, pady=label_pady)
        self.dr_time_label.grid(row=1, column=0, sticky='E', padx=label_padx, pady=label_pady)
        self.dr_latitude_label.grid(row=2, column=0, sticky='E', padx=label_padx, pady=label_pady)
        self.dr_longitude_label.grid(row=3, column=0, sticky='E', padx=label_padx, pady=label_pady)
        self.course_label.grid(row=4, column=0, sticky='E', padx=label_padx, pady=label_pady)
        self.speed_label.grid(row=5, column=0, sticky='E', padx=label_padx, pady=label_pady)


        # Grid entry fields
        self.dr_date_entry.grid(row=0, column=1, padx=entry_padx, pady=entry_pady)
        self.dr_time_entry.grid(row=1, column=1, padx=entry_padx, pady=entry_pady)
        self.dr_latitude_entry.grid(row=2, column=1, padx=entry_padx, pady=entry_pady)
        self.dr_longitude_entry.grid(row=3, column=1, padx=entry_padx, pady=entry_pady)
        self.course_entry.grid(row=4, column=1, padx=entry_padx, pady=entry_pady)
        self.speed_entry.grid(row=5, column=1, padx=entry_padx, pady=entry_pady)

        # Add invisible labels for alignment if needed
        self.invisble_label_dr = ttk.Label(self.dr_info_frame, text="",)
        self.invisble_label_dr.grid(row=6, column=0, padx=label_padx, pady=label_pady, sticky = 'NSEW')

        self.invisble_label_dr2 = ttk.Label(self.dr_info_frame, text="")
        self.invisble_label_dr2.grid(row=6, column=1, padx=label_padx, pady=label_pady, sticky = 'NSEW')

        self.invisble_label_dr3 = ttk.Label(self.dr_info_frame, text="")
        self.invisble_label_dr3.grid(row=6, column=2, padx=label_padx, pady=label_pady, sticky = 'NSEW')
        
      
        self.dr_info_frame.grid_columnconfigure(0, weight=1)
        self.dr_info_frame.grid_columnconfigure(1, weight=1)
        self.dr_info_frame.grid_columnconfigure(2, weight=1)
        # self.dr_info_frame.grid_columnconfigure(3, weight=1)
        # self.dr_info_frame.grid_columnconfigure(4, weight=1)
        # self.dr_info_frame.grid_columnconfigure(5, weight=1)

        # Adjust column and row weights for centering
        for i in range(6):  # Assuming 7 columns in total
            self.dr_info_frame.grid_rowconfigure(i, weight=1)
        

    def create_sextant_info_entry(self):
        
        # create labels
        self.index_error_label = ttk.Label(self.sextant_info_frame, text='Index Error :')
        self.height_of_eye_label = ttk.Label(self.sextant_info_frame, text='Height of Eye ft:')
        self.temperature_label = ttk.Label(self.sextant_info_frame, text='Temperature C:')
        self.pressure_label = ttk.Label(self.sextant_info_frame, text='Pressure mb:')
        
        # configure labels
        self.index_error_label.config(font=('Helvetica', 10, 'bold'), )
        self.height_of_eye_label.config(font=('Helvetica', 10, 'bold'), )
        self.temperature_label.config(font=('Helvetica', 10, 'bold'), )
        self.pressure_label.config(font=('Helvetica', 10, 'bold'), )

        
        # create string variables
        self.index_error = tk.StringVar(self)
        self.height_of_eye = tk.StringVar(self)
        self.temperature = tk.StringVar(self)
        self.pressure = tk.StringVar(self)

        # create entries
        self.index_error_entry = ttk.Entry(self.sextant_info_frame, 
                                           textvariable=self.index_error, 
                                           width=12,
                                           validate='focusout',
                                           validatecommand=(self.validate_number, '%P'))

        self.height_of_eye_entry = ttk.Entry(self.sextant_info_frame, 
                                             textvariable=self.height_of_eye, 
                                             width=12,
                                             validate='focusout',
                                             validatecommand=(self.validate_number, '%P'))

        self.temperature_entry = ttk.Entry(self.sextant_info_frame,
                                           width=12,
                                           textvariable=self.temperature, 
                                           validate='focusout',
                                           validatecommand=(self.validate_number, '%P'),
                                           text = '10.0'
                                           )
        

        self.pressure_entry = ttk.Entry(self.sextant_info_frame, 
                                        width=12,
                                        textvariable=self.pressure, 
                                        validate='focusout',
                                        validatecommand=(self.validate_number, '%P', ),
                                        text = '1010.0'
                                        )

        self.sextant_entry_fields = [self.index_error_entry,
                                    self.height_of_eye_entry,
                                    self.temperature_entry,
                                    self.pressure_entry] 

        # make the entry fields bold 
        for entry in self.sextant_entry_fields:
            entry.config(font=('Helvetica', 12, 'bold'), justify='center')
        
        label_padx = 10
        label_pady = 10
        entry_padx = 10
        entry_pady = 10


        # grid labels and entry fields, put in center of label frame
        self.index_error_label.grid(row=0, column=0, sticky='E', padx=label_padx, pady=label_pady)
        self.height_of_eye_label.grid(row=1, column=0, sticky='E', padx=label_padx, pady=label_pady)
        self.temperature_label.grid(row=2, column=0, sticky='E', padx=label_padx, pady=label_pady)
        self.pressure_label.grid(row=3, column=0, sticky='E', padx=label_padx, pady=label_pady)
        self.index_error_entry.grid(row=0, column=1, padx=entry_padx, pady=entry_pady)
        self.height_of_eye_entry.grid(row=1, column=1, padx=entry_padx, pady=entry_pady)
        self.temperature_entry.grid(row=2, column=1, padx=entry_padx, pady=entry_pady)
        self.pressure_entry.grid(row=3, column=1, padx=entry_padx, pady=entry_pady)

        # create invisible labels for alignment
        self.invisible_label3 = ttk.Label(self.sextant_info_frame, text="")
        self.invisible_label3.grid(row=4, column=0, padx=label_padx, pady=label_pady)

        self.invisible_label4 = ttk.Label(self.sextant_info_frame, text="")
        self.invisible_label4.grid(row=4, column=1, padx=label_padx, pady=label_pady)

        self.invisible_label5 = ttk.Label(self.sextant_info_frame, text="")
        self.invisible_label5.grid(row=4, column=2, padx=label_padx, pady=label_pady)


        # Adjust column and row weights for centering
        self.sextant_info_frame.grid_columnconfigure(0, weight=1)
        self.sextant_info_frame.grid_columnconfigure(1, weight=1)
        self.sextant_info_frame.grid_columnconfigure(2, weight=1)

        for i in range(4):  # Assuming 4 rows in total
            self.sextant_info_frame.grid_rowconfigure(i, weight=1)

    
    def create_sight_info_entry(self):
        """ 
        Creates labels and entry field for:
        Body : Autocomplete Entry
        Hs : Entry
        Date : Entry
        Time : Entry
        """
        # create labels
        self.body_label = ttk.Label(self.sight_info_entry_frame, text='Body:')
        self.hs_label = ttk.Label(self.sight_info_entry_frame, text='Hs:')
        self.date_label = ttk.Label(self.sight_info_entry_frame, text='Date:')
        self.time_label = ttk.Label(self.sight_info_entry_frame, text='Time:')

        # auto complete options
        named_bodies = ['SunLL', 'SunUL', 'MoonLL', 'MoonUL', 'Mars', 'Venus', 'Jupiter', 'Saturn']
        named_stars = [*cnav.Sight.named_star_dict]
        options = named_bodies + named_stars

        # create string variables
        self.body = tk.StringVar()
        self.hs = tk.StringVar()
        self.date = tk.StringVar()
        self.time = tk.StringVar()

        # create entry fields
        self.body_entry = AutocompleteCombobox(self.sight_info_entry_frame, completevalues=options, textvariable=self.body, width=10)
        self.hs_entry = ttk.Entry(self.sight_info_entry_frame, textvariable=self.hs, width=12)
        self.date_entry = ttk.Entry(self.sight_info_entry_frame, textvariable=self.date, width=12)
        self.time_entry = ttk.Entry(self.sight_info_entry_frame, textvariable=self.time, width=12)

        # sight entry fields
        self.sight_entry_fields = [self.body_entry, 
                                   self.hs_entry, 
                                   self.date_entry, 
                                   self.time_entry]

        # make the entry fields bold
        for entry in self.sight_entry_fields:
            entry.config(font=('Helvetica', 12, 'bold'), justify='center')
        
        # make the labels bold
        self.body_label.config(font=('Helvetica', 10, 'bold'))
        self.hs_label.config(font=('Helvetica', 10, 'bold'))
        self.date_label.config(font=('Helvetica', 10, 'bold'))
        self.time_label.config(font=('Helvetica', 10, 'bold'))

        # grid labels and entry fields, put in center of label frame
        self.body_label.grid(row=0, column=0, sticky='E', padx=10, pady=10)  # sticky changed to 'E' for right alignment
        self.hs_label.grid(row=1, column=0, sticky='E', padx=10, pady=10)
        self.date_label.grid(row=2, column=0, sticky='E', padx=10, pady=10)
        self.time_label.grid(row=3, column=0, sticky='E', padx=10, pady=10)
        self.body_entry.grid(row=0, column=1, padx=10, pady=10)  # removed sticky to allow natural width
        self.hs_entry.grid(row=1, column=1, padx=10, pady=10)
        self.date_entry.grid(row=2, column=1, padx=10, pady=10)
        self.time_entry.grid(row=3, column=1, padx=10, pady=10)

        # create add, update, and delete buttons
        self.add_button = ttk.Button(self.sight_info_entry_frame, text='Add', 
                                     command=lambda: add_new_sight(
                                            self,
                                            self.body_entry,
                                            [self.body_entry,
                                            self.hs_entry,
                                            self.date_entry,
                                            self.time_entry],
                                            self.sight_list_treeview
                                     ),
                                     style='Outline.TButton'

        )

        self.update_button = ttk.Button(self.sight_info_entry_frame, text='Update', 
                                        command=lambda: update_sight(
                                            [self.body_entry,
                                            self.hs_entry,
                                            self.date_entry,
                                            self.time_entry],
                                            self.sight_list_treeview
                                        ),
                                        style='Outline.TButton'
                                                                 
        )

        self.delete_button = ttk.Button(self.sight_info_entry_frame, text='Delete', 
                                        command = lambda: delete_sight(self.sight_list_treeview),
                                        style='Outline.TButton'
                                        
        )

         # grid buttons
        self.add_button.grid(row=4, column=0, sticky='NESW', padx=10, pady=10)
        self.update_button.grid(row=4, column=1, sticky='NESW', padx=10, pady=10)
        self.delete_button.grid(row=4, column=2, sticky='NESW', padx=10, pady=10)

        # Adjust column and row weights for centering
        self.sight_info_entry_frame.grid_columnconfigure(0, weight=1)
        self.sight_info_entry_frame.grid_columnconfigure(1, weight=1)
        self.sight_info_entry_frame.grid_columnconfigure(2, weight=1)

        for i in range(4):  # 5 rows in total
            self.sight_info_entry_frame.grid_rowconfigure(i, weight=1)


    def create_fix_info_entry(self):
        """
        Creates Treeview with fields for:
        Date, 
        Computed Lat
        Computed Long
        DR Lat
        DR Long
        """
        self.fix_info_frame = self.entry_page_4

        style = ttk.Style()
        style.configure('info.Treeview', rowheight=50) 

                # create treeview
        self.fix_treeview = ttk.Treeview(self.fix_info_frame, height=1, style = 'warning.Treeview')


        # add columns to treeview
        self.fix_treeview['columns'] = ('Date', 'Computed Lat', 'Computed Long', 'DR Lat', 'DR Long')
        self.fix_treeview.column('#0', width=0, stretch='no')
        self.fix_treeview.column('Date', anchor='center', width=220, stretch='yes')
        self.fix_treeview.column('Computed Lat', anchor='center', width=80)
        self.fix_treeview.column('Computed Long', anchor='center', width=80)
        self.fix_treeview.column('DR Lat', anchor='center', width=80)
        self.fix_treeview.column('DR Long', anchor='center', width=80)

        # add headings to treeview
        self.fix_treeview.heading('#0', text='', anchor='w')
        self.fix_treeview.heading('Date', text='Date', anchor='center')
        self.fix_treeview.heading('Computed Lat', text='Computed Lat', anchor='center')
        self.fix_treeview.heading('Computed Long', text='Computed Long', anchor='center')
        self.fix_treeview.heading('DR Lat', text='DR Lat', anchor='center')
        self.fix_treeview.heading('DR Long', text='DR Long', anchor='center')


               
        first_row_width = 10

        # create labels
        self.fix_date_label = ttk.Label(self.fix_info_frame, text='Fix Date UTC:')
        self.fix_time_label = ttk.Label(self.fix_info_frame, text='Fix Time UTC:')

        # configure labels 
        self.fix_date_label.config(font=('Helvetica', 10, 'bold'), foreground='orange')
        self.fix_time_label.config(font=('Helvetica', 10, 'bold'), foreground='orange')


        # create string variables 
        self.fix_date = tk.StringVar(self)
        self.fix_time = tk.StringVar(self)

        # create entries
        self.fix_date_entry = ttk.Entry(self.fix_info_frame,
                                        width=first_row_width,
                                        textvariable=self.fix_date,
                                        validate='focusout',
                                        validatecommand=(self.check_date_format, '%P')
                                        )

        self.fix_time_entry = ttk.Entry(self.fix_info_frame, 
                                        width=first_row_width,
                                        textvariable=self.fix_time,
                                        validate='focusout',
                                        validatecommand=(self.check_time_format, '%P')
                                        )
        
        self.fix_entry_fields = [self.fix_date_entry,
                                 self.fix_time_entry]
        
        # grid entries 
        self.fix_date_entry.grid(row=0, column=1, padx=10, pady=10)
        self.fix_time_entry.grid(row=1, column=1, padx=10, pady=10)

        # make the entry fields bold
        for entry in self.fix_entry_fields:
            entry.config(font = ('Helvetica', 12, 'bold'), justify = 'center')

        # make the labels bold
        self.fix_date_label.config(font=('Helvetica', 10, 'bold'))
        self.fix_time_label.config(font=('Helvetica', 10, 'bold'))

        # grid labels and entry fields, put in center of label frame
        self.fix_date_label.grid(row=0, column=0, sticky='E', padx=10, pady=10)
        self.fix_time_label.grid(row=1, column=0, sticky='E', padx=10, pady=10)

        
        # create ttk meter
        from ttkbootstrap.widgets import Progressbar
        self.meter = Floodgauge(self.fix_info_frame, value = 0, mode = 'determinate', maximum = 100, bootstyle = 'success', mask = "Fix Confidence: {}%", )

        # grid meter
        self.meter.grid(row=2, column=0, padx=10, pady=10, columnspan=5, sticky='nsew')
        
        
        # create compute fix button
        self.compute_fix_button = ttk.Button(self.fix_info_frame, text='Compute Fix', 
                                             command=self.on_compute_fix_button_click, style = 'Outline.TButton')
        


        # Place Treeview in the next row, spanning across all columns
        self.fix_treeview.grid(row=3, column=0, padx=10, pady=10, columnspan=5, sticky='nsew')

        # Compute Fix Button
        self.compute_fix_button.grid(row=4, column=0, padx=10, pady=10, columnspan=5, sticky='nsew')


        # Adjust column and row weights for centering
        self.fix_info_frame.grid_columnconfigure(0, weight=1)
        self.fix_info_frame.grid_columnconfigure(1, weight=1)
        self.fix_info_frame.grid_columnconfigure(2, weight=1)

        # Adjust column and row weights for centering
        for i in range(5):  # Assuming 4 rows in total
            self.fix_info_frame.grid_rowconfigure(i, weight=1)


    def aggregate_entry_fields(self):
        self.fields = self.dr_entry_fields + self.sextant_entry_fields + self.fix_entry_fields
        
        return self.fields

    def on_compute_fix_button_click(self):

        reduction_instance = CapellaSightReduction(
        self.fields,
        [self.sight_list_treeview,
        self.fix_treeview],
        self.meter
    )
        self.master.page2.refresh_figure()
        self.master.page3.refresh_figure()


           
    def autocompletion_binding(self):
        # instantiate autocompletion class
        self.autocomplete = AutoComplete(self.master)

        # bind autocompletion to DR entry fields
        self.dr_date_entry.bind('<KeyRelease>', lambda event: self.autocomplete.date_formatting(event, self.dr_date_entry))

        self.dr_time_entry.bind('<KeyRelease>', lambda event: self.autocomplete.time_formatting(event, self.dr_time_entry))

        self.dr_latitude_entry.bind('<KeyRelease>', lambda event: self.autocomplete.lat_formatting(event, self.dr_latitude_entry))

        self.dr_longitude_entry.bind('<KeyRelease>', lambda event: self.autocomplete.long_formatting(event, self.dr_longitude_entry))

        self.hs_entry.bind('<KeyRelease>', lambda event: self.autocomplete.hs_formatting(event, self.hs_entry))

        

        # bind autocompletion to sight entry fields
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
        # create update button tooltip
        self.update_button_tooltip = ToolTip(self.update_button, self.extractor.get_text('updating_a_sight'))

        # create delete button tooltip
        self.delete_button_tooltip = ToolTip(self.delete_button, self.extractor.get_text('deleting_a_sight'))

        # create add button tooltip
        self.add_button_tooltip = ToolTip(self.add_button, self.extractor.get_text('adding_a_sight'))

        # create tooltip for DR info frame
        self.dr_info_frame_tooltip = ToolTip(self.dr_info_frame, self.extractor.get_text('setting_a_dr'))
        
        # create tooltop for sextant info frame
        self.sextant_info_toolop = ToolTip(self.sextant_info_frame, self.extractor.get_text('adding_sextant_info')) 
        
        # create tooltip for fix info frame
        self.fix_info_frame_tooltip = ToolTip(self.fix_info_frame, self.extractor.get_text('computing_a_fix'))
        

    
