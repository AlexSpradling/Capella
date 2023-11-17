import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.tooltip import ToolTip
from ttkwidgets.autocomplete import AutocompleteCombobox
import utilities.celestial_engine as cnav
from utilities.sight_handling import add_new_sight, delete_sight, update_sight, UpdateAndAveraging
from utilities.reduce_sight import CapellaSightReduction
from utilities.input_checking import InputChecking
from utilities.autocompletion import AutoComplete
from utilities.sight_planning import SightSessionPlanning
from utilities.tooltips import TextExtractor

class SightEntryPage(ttk.Frame):
    
    # sight treeview class variable
    counter = 0
    def __init__(self, container):
        super().__init__(container)

        self.create_label_frames()
        self.create_sight_treeview()
        self.create_dr_info_entry()
        self.create_sight_info_entry()
        self.create_fix_info_treeview()
        self.create_compute_fix_button() 
        self.autocompletion_binding()
        self.create_tooltips()


        # binds 
        self.sight_list_treeview.bind('<<TreeviewSelect>>', 
                                      lambda event: UpdateAndAveraging(self.sight_list_treeview,
                                                                       self.sight_entry_fields 
                                                                       ).print_element(event))
  
    def create_label_frames(self):

        self.sight_frame = ttk.LabelFrame(self, text='Sight')
        self.dr_info_frame = ttk.LabelFrame(self, text='DR Info')
        self.sextant_info_frame = ttk.LabelFrame(self, text='Sextant Info')
        self.sight_info_entry_frame = ttk.LabelFrame(self, text='Sight Info')
        self.fix_info_frame = ttk.LabelFrame(self, text='Fix Info')
        
        # Arrange label frames using grid
        self.sight_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        self.dr_info_frame.grid(row=1, column=0, padx=10, pady=10, sticky='ew')
        self.sextant_info_frame.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
        self.sight_info_entry_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='ew')
        self.fix_info_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        
        # Make columns expandable
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Adjust row weights to give sight_frame more space
        self.grid_rowconfigure(0, weight=2)  # sight_frame gets twice as much space
        self.grid_rowconfigure(3, weight=1)  # fix_info_frame

    def create_sight_treeview(self):

        # create treeview
        self.sight_list_treeview = ttk.Treeview(self.sight_frame, height=10)

        # pack 
        self.sight_list_treeview.pack(padx=10, pady=10, fill='both', expand=True, anchor= 'center')

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
            Course
            Speed
            Index Error
            Height of Eye
            Temperature
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

        self.index_error_label = ttk.Label(self.sextant_info_frame, text='Index Error :')
        self.height_of_eye_label = ttk.Label(self.sextant_info_frame, text='Height of Eye ft:')
        self.temperature_label = ttk.Label(self.sextant_info_frame, text='Temperature C:')
        self.pressure_label = ttk.Label(self.sextant_info_frame, text='Pressure mb:')
        self.fix_date_label = ttk.Label(self.fix_info_frame, text='Fix Date UTC:')
        self.fix_time_label = ttk.Label(self.fix_info_frame, text='Fix Time UTC:')

        # make date, time, latitude and longitude, speed and course labels bold and green
        self.dr_date_label.config(font=('Helvetica', 10, 'bold'), foreground='green')
        self.dr_time_label.config(font=('Helvetica', 10, 'bold'), foreground='green')
        self.dr_latitude_label.config(font=('Helvetica', 10, 'bold'), foreground='green')
        self.dr_longitude_label.config(font=('Helvetica', 10, 'bold'), foreground='green')
        self.course_label.config(font=('Helvetica', 10, 'bold'), foreground='green')
        self.speed_label.config(font=('Helvetica', 10, 'bold'), foreground='green')
        
        # make the rest of the labels bold and blue
        self.index_error_label.config(font=('Helvetica', 10, 'bold'), )
        self.height_of_eye_label.config(font=('Helvetica', 10, 'bold'), )
        self.temperature_label.config(font=('Helvetica', 10, 'bold'), )
        self.pressure_label.config(font=('Helvetica', 10, 'bold'), )
        self.fix_date_label.config(font=('Helvetica', 10, 'bold'), foreground='orange')
        self.fix_time_label.config(font=('Helvetica', 10, 'bold'), foreground='orange')

        # create string variables
        self.dr_date = tk.StringVar(self)
        self.dr_time = tk.StringVar(self)
        self.dr_latitude = tk.StringVar(self)
        self.dr_longitude = tk.StringVar(self)
        self.course = tk.StringVar(self)
        self.speed = tk.StringVar(self)
        self.index_error = tk.StringVar(self)
        self.height_of_eye = tk.StringVar(self)
        self.temperature = tk.StringVar(self)
        self.pressure = tk.StringVar(self)
        self.fix_date = tk.StringVar(self)
        self.fix_time = tk.StringVar(self)

        # create validation command instance 
        self.validate_number = self.register(InputChecking.validate_number)
        self.check_time_format = self.register(InputChecking.check_time_format)
        self.check_date_format = self.register(InputChecking.check_date_format)
        self.check_hs_format = self.register(InputChecking.check_hs_format)
        self.check_lat_format = self.register(InputChecking.check_lat_format)
        self.check_long_format = self.register(InputChecking.check_long_format)


        # create entry fields
        first_row_width = 12
        second_row_width = 4
        third_row_width = 9

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

        self.index_error_entry = ttk.Entry(self.sextant_info_frame, 
                                           textvariable=self.index_error, 
                                           width=second_row_width,
                                           validate='focusout',
                                           validatecommand=(self.validate_number, '%P'))

        self.height_of_eye_entry = ttk.Entry(self.sextant_info_frame, 
                                             textvariable=self.height_of_eye, 
                                             width=second_row_width,
                                             validate='focusout',
                                             validatecommand=(self.validate_number, '%P'))

        self.temperature_entry = ttk.Entry(self.sextant_info_frame,
                                           width=second_row_width,
                                           textvariable=self.temperature, 
                                           validate='focusout',
                                           validatecommand=(self.validate_number, '%P'),
                                           text = '10.0'
                                           )
        

        self.pressure_entry = ttk.Entry(self.sextant_info_frame, 
                                        width=second_row_width,
                                        textvariable=self.pressure, 
                                        validate='focusout',
                                        validatecommand=(self.validate_number, '%P', ),
                                        text = '1010.0'
                                        )

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

        self.entry_fields = [self.dr_date_entry, 
                             self.dr_time_entry, 
                             self.dr_latitude_entry, 
                             self.dr_longitude_entry,
                             self.course_entry, 
                             self.speed_entry, 
                             self.index_error_entry, 
                             self.height_of_eye_entry,
                             self.temperature_entry, 
                             self.pressure_entry, 
                             self.fix_date_entry, 
                             self.fix_time_entry]
        
        self.dr_text_variables = [self.dr_date, 
                                  self.dr_time, 
                                  self.dr_latitude, 
                                  self.dr_longitude, 
                                  self.course, 
                                  self.speed, 
                                  self.index_error, 
                                  self.height_of_eye, 
                                  self.temperature, 
                                  self.pressure, 
                                  self.fix_date, 
                                  self.fix_time]
        
        # make the entry fields bold 
        for entry in self.entry_fields:
            entry.config(font=('Helvetica', 10, 'bold'), justify='center')
        
        

        # grid labels
        self.dr_date_label.grid(row=0, column=0, sticky='NSW', padx=10, pady=10, )
        self.dr_time_label.grid(row=1, column=0, sticky='NSW', padx=10, pady=10)
        self.dr_latitude_label.grid(row=2, column=0, sticky='NSW', padx=10, pady=10)
        self.dr_longitude_label.grid(row=3, column=0, sticky='NSW', padx=10, pady=10)
        self.course_label.grid(row=0, column=2, sticky='NSW', padx=10, pady=10)
        self.speed_label.grid(row=1, column=2, sticky='NSW', padx=10, pady=10)

        self.index_error_label.grid(row=0, column=0, sticky='NSW', padx=10, pady=10)
        self.height_of_eye_label.grid(row=1, column=0, sticky='NSW', padx=10, pady=10)
        self.temperature_label.grid(row=2, column=0, sticky='NSW', padx=10, pady=10)
        self.pressure_label.grid(row=3, column=0, sticky='NSW', padx=10, pady=10)
        

        

        # grid entry fields
        self.dr_date_entry.grid(row=0, column=1, sticky='NESW', padx=10, pady=10)
        self.dr_time_entry.grid(row=1, column=1, sticky='NESW', padx=10, pady=10)
        self.dr_latitude_entry.grid(row=2, column=1, sticky='NESW', padx=10, pady=10)
        self.dr_longitude_entry.grid(row=3, column=1, sticky='NESW', padx=10, pady=10)
        self.course_entry.grid(row=0, column=3, sticky='NESW', padx=10, pady=10)
        self.speed_entry.grid(row=1, column=3, sticky='NESW', padx=10, pady=10)

        self.index_error_entry.grid(row=0, column=1, sticky='NS', padx=10, pady=10)
        self.height_of_eye_entry.grid(row=1, column=1, sticky='NS', padx=10, pady=10)
        self.temperature_entry.grid(row=2, column=1, sticky='NS', padx=10, pady=10)
        self.pressure_entry.grid(row=3, column=1, sticky='NS', padx=10, pady=10)
        # self.fix_date_entry.grid(row=0, column=3, sticky='NS', padx=10, pady=10)
        # self.fix_time_entry.grid(row=1, column=3, sticky='NS', padx=10, pady=10)

        


              
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
        self.sight_entry_fields = [self.body_entry, self.hs_entry, self.date_entry, self.time_entry]

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

        for i in range(5):  # 5 rows in total
            self.sight_info_entry_frame.grid_rowconfigure(i, weight=1)


    def create_fix_info_treeview(self):
        """
        Creates Treeview with fields for:
        Date, 
        Computed Lat
        Computed Long
        DR Lat
        DR Long
        """

        # create treeview
        self.fix_treeview = ttk.Treeview(self.fix_info_frame, height=2)

        # add columns to treeview
        self.fix_treeview['columns'] = ('Date', 'Computed Lat', 'Computed Long', 'DR Lat', 'DR Long')
        self.fix_treeview.column('#0', width=0, stretch='no')
        self.fix_treeview.column('Date', anchor='center', width=110)
        self.fix_treeview.column('Computed Lat', anchor='center', width=100)
        self.fix_treeview.column('Computed Long', anchor='center', width=100)
        self.fix_treeview.column('DR Lat', anchor='center', width=100)
        self.fix_treeview.column('DR Long', anchor='center', width=100)

        # add headings to treeview
        self.fix_treeview.heading('#0', text='', anchor='w')
        self.fix_treeview.heading('Date', text='Date', anchor='center')
        self.fix_treeview.heading('Computed Lat', text='Computed Lat', anchor='center')
        self.fix_treeview.heading('Computed Long', text='Computed Long', anchor='center')
        self.fix_treeview.heading('DR Lat', text='DR Lat', anchor='center')
        self.fix_treeview.heading('DR Long', text='DR Long', anchor='center')

        # Configure the column weights of fix_info_frame.
        self.fix_info_frame.grid_columnconfigure(0, weight=0)  # Fix date label column
        self.fix_info_frame.grid_columnconfigure(1, weight=0)  # Fix date entry column
        self.fix_info_frame.grid_columnconfigure(2, weight=0)  # Fix time label column
        self.fix_info_frame.grid_columnconfigure(3, weight=0)  # Fix time entry column
        self.fix_info_frame.grid_columnconfigure(4, weight=1)  # Remaining space for Treeview

        # Labels
        self.fix_date_label.grid(row=0, column=0, sticky='NSW', padx=5, pady=10)
        self.fix_date_entry.grid(row=0, column=1, sticky='NSW', padx=5, pady=10)
        self.fix_time_label.grid(row=0, column=2, sticky='NSW', padx=5, pady=10)
        self.fix_time_entry.grid(row=0, column=3, sticky='NSW', padx=5, pady=10)

        # Place Treeview in the next row, spanning across all columns
        self.fix_treeview.grid(row=1, column=0, padx=10, pady=10, columnspan=5, sticky='nsew')



    def create_compute_fix_button(self):
        """
        Creates Compute Fix button
        """
        self.compute_fix_button = ttk.Button(self.fix_info_frame, text='Compute Fix', 
                                             command=self.on_compute_fix_button_click, style = 'Outline.TButton')
        # Compute Fix Button
        self.compute_fix_button.grid(row=2, column=0, padx=10, pady=10, columnspan=5, sticky='nsew')

    def on_compute_fix_button_click(self):
        CapellaSightReduction(
        self.entry_fields,
        [self.sight_list_treeview,
        self.fix_treeview]
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
        self.extractor = TextExtractor('text_files/tooltips.txt') 
        # create update button tooltip
        self.update_button_tooltip = ToolTip(self.update_button, self.extractor.get_text('updating_a_sight'))

        # create delete button tooltip
        self.delete_button_tooltip = ToolTip(self.delete_button, self.extractor.get_text('deleting_a_sight'))

        # create add button tooltip
        self.add_button_tooltip = ToolTip(self.add_button, self.extractor.get_text('adding_a_sight'))

        # create tooltip for DR info frame
        self.dr_info_frame_tooltip = ToolTip(self.dr_info_frame, self.extractor.get_text('setting_a_dr'))
        
    


    
