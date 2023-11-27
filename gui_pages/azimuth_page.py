import tkinter as tk
import ttkbootstrap as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import datetime as dt
from ttkwidgets.autocomplete import AutocompleteCombobox
import utilities.celestial_engine as cnav
from ttkbootstrap.dialogs import Messagebox
from tkinter import simpledialog
import numpy as np
import geomag as gm
from skyfield.api import Angle, utc
from utilities.autocompletion import AutoComplete

class AzimuthPage(ttk.Frame):
    
    def __init__(self, container):
        super().__init__(container)
        self.init_widgets()

    def init_widgets(self):
        self.create_label_frames()
        self.create_observation_inputs()
        self.create_treeview()
        self.autocompletion_binding()

    def create_label_frames(self):
        self.azwrap = ttk.LabelFrame(self, text='Compass Observations Records')
        self.azwrap2 = ttk.LabelFrame(self, text='Observation Input')
        self.azwrap.pack(fill='both', expand=True, padx=10, pady=10)
        self.azwrap2.pack(expand=True, padx=10, pady=10)

        # self.azwrap.grid(row=0, column=0, sticky='NESW')
        # self.azwrap2.grid(row=1, column=0, sticky='NESW')

        # weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        

    def create_observation_inputs(self):
        # Define unique StringVar variables for each input
        self.az_vars = [tk.StringVar(self) for _ in range(12)]

        self.populate_dropdown()
        self.populate_entries()

        compute_btn = ttk.Button(self.azwrap2, text="COMPUTE", command=self.compass_correction, style='primary.Outline.TButton')
        compute_btn.grid(row=6, column=0, padx=10, pady=10)
        compute_btn.configure(width='12')

    def populate_dropdown(self):
        named_bodies = ['Pier Hdg', 'SunLL', 'SunUL', 'MoonLL', 'MoonUL', 'Mars', 'Venus', 'Jupiter', 'Saturn']
        named_stars = [*cnav.Sight.named_star_dict]
        options = named_bodies + named_stars

        azlbl1 = ttk.Label(self.azwrap2, text="Body", width=10, anchor='w')
        azlbl1.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        self.azbodies = AutocompleteCombobox(self.azwrap2, textvariable=self.az_vars[0], completevalues=options, width=12)
        self.azbodies['values'] = options
        self.azbodies.grid(row=0, column=1, padx=10, pady=10)

        # make AutoComplete Combobox helvetica, 10, bold
        azlbl1.configure(font=('Helvetica', 10, 'bold'))
        self.azbodies.configure(font=('Helvetica', 10, 'bold'))

        # Bind the event for value change
        self.azbodies.bind("<<ComboboxSelected>>", self.on_combobox_selected)

    def on_combobox_selected(self, event):
        selected_value = self.azbodies.get()
        if selected_value == "Pier Hdg":
            heading = simpledialog.askfloat("Input", "Enter the heading:")
            if heading is not None:
                # Set the heading value to the combobox
                self.azbodies.set(heading)
            else:
                Messagebox.showwarning("Warning", "No heading entered.")
        
    def populate_entries(self):
        labels_texts = ["Gryo Hd", "Mag Hd", "Gyro Obsv."]
        default_values = ['300', '300', '300']

        for idx, (label_text, default_value) in enumerate(zip(labels_texts, default_values)):
            lbl = ttk.Label(self.azwrap2, text=label_text, width=10, anchor='w')
            lbl.grid(row=idx + 1, column=0, padx=10, pady=10, sticky='w')

            ent = ttk.Entry(self.azwrap2, textvariable=self.az_vars[idx + 1], width=20)
            # make entries helvetica, 10, bold
            ent.configure(font=('Helvetica', 10, 'bold'))
            ent.insert(0, default_value)
            ent.grid(row=idx + 1, column=1, padx=10, pady=10)
            # make labels helvetica, 10, bold
            lbl.configure(font=('Helvetica', 10, 'bold'))

        date_label = ttk.Label(self.azwrap2, text="Date UTC", width=10, anchor='w')
        date_label.grid(row=0, column=2, padx=10, pady=10, sticky='w')
        self.date_entry = ttk.Entry(self.azwrap2, textvariable=self.az_vars[8], width=20)
        self.date_entry.grid(row=0, column=3, padx=10, pady=10)
        self.date_entry.insert(0, dt.datetime.utcnow().strftime('%Y-%m-%d'))

        time_label = ttk.Label(self.azwrap2, text="Time UTC", width=10, anchor='w')
        time_label.grid(row=1, column=2, padx=10, pady=10, sticky='w')
        self.time_entry = ttk.Entry(self.azwrap2, textvariable=self.az_vars[9], width=20)
        self.time_entry.grid(row=1, column=3, padx=5, pady=3)
        self.time_entry.insert(0, dt.datetime.utcnow().strftime('%H:%M:%S'))

        lat_label = ttk.Label(self.azwrap2, text="DR Lat", width=10, anchor='w')
        lat_label.grid(row=2, column=2, padx=10, pady=10, sticky='w')
        self.lat_entry = ttk.Entry(self.azwrap2, textvariable=self.az_vars[10], width=20)
        self.lat_entry.grid(row=2, column=3, padx=5, pady=3)

        lon_label = ttk.Label(self.azwrap2, text="DR Long", width=10, anchor='w')
        lon_label.grid(row=3, column=2, padx=10, pady=10, sticky='w')
        self.lon_entry = ttk.Entry(self.azwrap2, textvariable=self.az_vars[11], width=20)
        self.lon_entry.grid(row=3, column=3, padx=10, pady=10)

        # make labels helvetica, 10, bold
        date_label.configure(font=('Helvetica', 10, 'bold'))
        time_label.configure(font=('Helvetica', 10, 'bold'))
        lat_label.configure(font=('Helvetica', 10, 'bold'))
        lon_label.configure(font=('Helvetica', 10, 'bold'))
        

        # make entries helvetica, 10, bold  
        self.date_entry.configure(font=('Helvetica', 10, 'bold'))
        self.time_entry.configure(font=('Helvetica', 10, 'bold'))
        self.lat_entry.configure(font=('Helvetica', 10, 'bold'))
        self.lon_entry.configure(font=('Helvetica', 10, 'bold'))
        
        # make autocomplete combobox helvetica, 10
        self.azbodies.configure(font=('Helvetica', 10))



    def create_treeview(self):
        self.trvaz = ttk.Treeview(self.azwrap, show='headings', height='12')
        self.trvaz.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        self.trvaz['columns'] = [str(i) for i in range(1, 14)]
        
        columns_width = [69, 60, 62, 66, 47, 48, 48, 48, 48, 54, 54, 54, 50]
        for col, width in zip(self.trvaz['columns'], columns_width):
            self.trvaz.column(col, anchor='center', width=width)

        headings = ["Date", 'G.M.T.', 'L', "λ", "G Hd", "C Hd", "T Brg", "G Brg", "Obj", "G Err", "C Err", "Var", "Dev"]
        for col, heading in zip(self.trvaz['columns'], headings):
            self.trvaz.heading(col, text=heading)

    def compass_correction(self):
        year, month, day = self.az_vars[8].get().split('-')
        hour, minute, second = self.az_vars[9].get().split(':')
        datetimeaz = dt.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), tzinfo=utc)

        latitude = self.parse_lat_lon(self.az_vars[10].get())
        longitude = self.parse_lat_lon(self.az_vars[11].get())

        body = self.az_vars[0].get()

        try:
            az = float(body)  # Try to convert body to a float (to check if it's a Pier Heading number)
        except ValueError:
            if body == 'Pier Hdg':
                pier_heading = simpledialog.askfloat("Input", "Enter Pier Heading:")
                if pier_heading is not None:
                    self.azbodies.set(pier_heading)  # Update the combobox value
                    az = pier_heading
                else:
                    Messagebox.showwarning('Input Error', 'Enter Pier Heading')
                    return
            else:
                ephem = cnav.Utilities.get_gha_dec(body, datetimeaz, latitude, longitude)
                az = ephem[4].degrees

        gyro_hd = float(self.az_vars[1].get())
        std_hd = float(self.az_vars[2].get())
        gyro_az = float(self.az_vars[3].get())
        variation = np.round(float(gm.declination(latitude, longitude, 0)), 1)

        gyro_error = np.round(float(gyro_az - az), 1) if body != 'Pier Hdg' else np.round(float(gyro_az - az), 1)
        gyro_error_str = self.format_direction(gyro_error, 'E', 'W')
        deviation = np.round(gyro_hd - gyro_error - variation - std_hd, 1)
        com_error = np.round(variation + deviation, 1)

        az_date = datetimeaz.strftime("%Y-%m-%d")
        az_time = datetimeaz.strftime("%H:%M:%S")
        az_lat = cnav.Utilities.print_position(latitude, latitude=True)
        az_lon = cnav.Utilities.print_position(longitude, latitude=False)
        var_str = self.format_direction(variation)
        dev_str = self.format_direction(deviation)
        com_error_str = self.format_direction(com_error)

        for i in self.trvaz.get_children():
            self.trvaz.delete(i)
        trvazstr = [az_date, az_time, az_lat, az_lon, gyro_hd, std_hd, np.round(az, 1) if body != 'Pier Hdg' else np.round(az, 1), gyro_az, body, gyro_error_str, com_error_str, var_str, dev_str]

        # small font 
        self.trvaz.tag_configure('small', font=('Verdana', 7))
        self.trvaz.insert('', 'end', text='', iid=0, values=trvazstr, tags=('small',))

    def parse_lat_lon(self, value):
        deg, minutes, direction = value.split('-')
        return (float(deg) + (float(minutes) / 60)) * (-1 if direction in ['S', 'W'] else 1)

    def format_direction(self, value, positive='E', negative='W'):
        return f'{abs(value)} {positive if value >= 0 else negative}'
    
    def autocompletion_binding(self):
        # initialize the autocomplete
        self.autocomplete = AutoComplete(self.master)

        self.lat_entry.bind("<KeyRelease>", lambda event: self.autocomplete.lat_formatting(event, self.lat_entry))

        self.lon_entry.bind("<KeyRelease>", lambda event: self.autocomplete.long_formatting(event, self.lon_entry))

        self.time_entry.bind("<KeyRelease>", lambda event: self.autocomplete.time_formatting(event, self.time_entry))

        self.date_entry.bind("<KeyRelease>", lambda event: self.autocomplete.date_formatting(event, self.date_entry))

