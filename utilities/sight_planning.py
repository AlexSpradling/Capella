import utilities.celestial_engine as cnav
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from collections import Counter
import datetime as dt
from tabulate import tabulate
import pyperclip as pc

class SightSessionPlanning():
    def __init__(self, ents, treeviews, fields):
    
        # page 1 date, time, latitude, longitude, course, speed entries
        self.ent_date = ents[0].get()
        self.ent_time = ents[1].get()
        self.ent_latitude = ents[2].get()
        self.ent_longitude = ents[3].get()
        self.ent_course = ents[4].get()
        self.ent_speed = ents[5].get()

        # page 4 date, time, latitude, longitude entry fields
        self.dr_date_entry = fields[0]
        self.dr_time_entry = fields[1]
        self.dr_latitude_entry = fields[2]
        self.dr_longitude_entry = fields[3]

        # values 
        self.dr_date_entry_value = fields[0].get()
        self.dr_time_entry_value = fields[1].get()
        self.dr_latitude_entry_value = fields[2].get()
        self.dr_longitude_entry_value = fields[3].get()

        # page 4 treeviews
        self.treeviews = treeviews

        self.delete_treeviews()
        self.update_treeviews()
        self.dr_sight_planning()
        self.visible_bodies_sorted_triads(self.ent_time, self.latitude, self.longitude)
        self.print_planning_info()

    def delete_treeviews(self):
        # delete any values in treeviews
        for treeview in self.treeviews:
            treeview.delete(*treeview.get_children())
    
    def update_treeviews(self):
        
        try:
            # convert to dd-mm.t format 
            self.latitude = cnav.Utilities.hmt_str_to_decimal_d(self.ent_latitude, self.ent_longitude)[0]
            self.longitude = cnav.Utilities.hmt_str_to_decimal_d(self.ent_longitude, self.ent_longitude)[1]

            
            # get phenomena times
            self.phenomena_times = cnav.Utilities.time_of_phenomena(self.ent_date, 
                                                                    self.ent_time, 
                                                                    self.latitude, 
                                                                    self.longitude,
                                                                    self.ent_course, 
                                                                    self.ent_speed)
            # add times of phenomena to treeview
            for element in self.phenomena_times:
                # make helvetica, 10, bold
                self.treeviews[0].tag_configure('bold', font=('Helvetica', 10, 'bold'))
                self.treeviews[0].insert('', 'end', text='', iid = element, values=element, tags=('bold',))
        except:
            Messagebox.show_error('Make sure the DR values are entered on page 1!', title = 'Incomplete DR Data')

    
    def dr_sight_planning(self):
        
        # delete any values in DR entry fields
        self.dr_latitude_entry.delete(0, 'end')
        self.dr_longitude_entry.delete(0, 'end')

        # get time from DR page and entry from sight planning page
        self.datetime_dr_start = cnav.Utilities.datetime(self.ent_date, self.ent_time)
        self.datetime_dr_end = cnav.Utilities.datetime(self.dr_date_entry_value, self.dr_time_entry_value)

        # get timedelta in seconds
        self.timedelta = dt.timedelta.total_seconds(self.datetime_dr_end - self.datetime_dr_start)

        # format latitude and longitude
        self.dr_lat_start = cnav.Utilities.hmt_str_to_decimal_d(self.ent_latitude, self.ent_longitude)[0]
        self.dr_long_start = cnav.Utilities.hmt_str_to_decimal_d(self.ent_longitude, self.ent_longitude)[1]

        # calculate DR position
        self.dr_lat_end = cnav.DRCalc(self.dr_lat_start, self.dr_long_start, self.timedelta, float(self.ent_course), float(self.ent_speed)).drlatfwds
        self.dr_long_end = cnav.DRCalc(self.dr_lat_start, self.dr_long_start, self.timedelta, float(self.ent_course), float(self.ent_speed)).drlongfwds

        # insert DR position into entry fields
        self.dr_latitude_entry.insert(0, cnav.Utilities.print_position2(self.dr_lat_end, latitude=True))
        self.dr_longitude_entry.insert(0, cnav.Utilities.print_position2(self.dr_long_end, latitude=False))


            
    def visible_bodies_sorted_triads(self, datetime, latitude, longitude):
            """Function to find all visible celestial bodies at the time requested, and sort them into weighted
            triads based on azimuth and magnitude """

            datetime = cnav.Utilities.datetime(self.ent_date, self.ent_time)
            possibleobvs = []
            named_bodies = ['SunLL', 'SunUL', 'MoonLL', 'MoonUL', 'Mars', 'Venus', 'Jupiter', 'Saturn']
            named_stars = [*cnav.Sight.named_star_dict]
            options = named_bodies + named_stars

            for body in options:
                ephem = cnav.Utilities.get_gha_dec(body, datetime, latitude, longitude)
                obsv = (body, ephem[3].degrees, ephem[4].degrees, ephem[5])
                # constrain to visible bodies that are easily shot
                if 10 < obsv[1] < 65:
                    obsv = (body, cnav.Utilities.hmt_str(ephem[3].degrees), round(ephem[4].degrees), ephem[5])
                    possibleobvs.append(obsv)

            triads = []
            # iterative process to create triad groupings
            for i in range(len(possibleobvs)):
                one = possibleobvs[i]
                try:
                    for x in range(len(possibleobvs)):
                        difference = (possibleobvs[i][2] - possibleobvs[x][2]) % 360
                        if difference > 115 and difference < 130:
                            two = possibleobvs[x]
                            for y in range(len(possibleobvs)):
                                difference2 = (possibleobvs[x][2] - possibleobvs[y][2]) % 360
                                if difference2 > 115 and difference2 < 130:
                                    three = possibleobvs[y]
                                    triad = [one, two, three]
                                    triads.append(triad)
                except:
                    pass

            sorted_triads = sorted(triads, key=lambda x: (x[0][3] + x[1][3] + x[2][3]) / 3)
            triad_bodies = []
            for i in range(len(sorted_triads)):
                body_list = (sorted_triads[i][0][0], sorted_triads[i][1][0], sorted_triads[i][2][0])
                triad_bodies.append(body_list)

            seen = set()

            triad_results = []
            for lst in triads:
                current = frozenset(Counter(lst).items())
                if current not in seen:
                    triad_results.append(lst)
                    seen.add(current)

            for i in possibleobvs:
                # make helvetica, 10, bold
                self.treeviews[1].tag_configure('bold', font=('Helvetica', 10, 'bold'))
                self.treeviews[1].insert('', 'end', text='', iid=i, values=i, tags=('bold',))
            counter = 0

            i = 1
            while i < len(triad_results):
                triad_results.insert(i, ('-'))
                i += (1 + 1)

            for i in triad_results:
                for y in i:
                    # make helvetica, 10, bold
                    self.treeviews[2].tag_configure('bold', font=('Helvetica', 10, 'bold'))
                    self.treeviews[2].insert('', 'end', text='', iid=counter, values=y, tags=('bold',))
                    counter += 1
            return
            
    def print_planning_info(self):
        """Aggregates all of the planning information and consolidates it into a printable format"""
        # get times of phenomena
        self.phenomena_times = cnav.Utilities.time_of_phenomena(self.ent_date, 
                                                                self.ent_time, 
                                                                self.latitude, 
                                                                self.longitude,
                                                                self.ent_course, 
                                                                self.ent_speed) 

        # make a markdown table using tabulate, get headers from treeviews[0]
        
        # get headers from treeview
        self.phenomena_headers = ['Date GMT', 'Date LMT', 'Event']

        # get values from treeview
        self.values = []
        for child in self.treeviews[0].get_children():
            self.values.append(self.treeviews[0].item(child)['values'])

        # create table
        self.table = tabulate(self.values, headers = self.phenomena_headers, tablefmt='github')

        # get visible bodies
        self.visible_bodies_headers = ['Body', 'Azimuth', 'Altitude', 'Magnitude']
        self.visible_bodies = []
        for child in self.treeviews[1].get_children():
            self.visible_bodies.append(self.treeviews[1].item(child)['values'])

        # create table
        self.table1 = tabulate(self.visible_bodies, headers = self.visible_bodies_headers, tablefmt='github')

        # get triads
        self.triad_headers = ['Body', 'Altitude', 'Azimuth', 'Magnitude'] 
        self.triads = []
        for child in self.treeviews[2].get_children():
            self.triads.append(self.treeviews[2].item(child)['values'])

        # create table
        self.table2 = tabulate(self.triads, headers = self.triad_headers, tablefmt='github')  

        # Header of planning information
        self.header = f"""\
        # Sight Planning Information
        ## Date: {self.ent_date}
        ## Time: {self.ent_time}
        ## Latitude: {self.ent_latitude}
        ## Longitude: {self.ent_longitude}
        ## Course: {self.ent_course}
        ## Speed: {self.ent_speed}
        """
        # copy to clipboard using pyperclip
        self.planning_info = self.header + '\n'*3 + self.table + '\n'*3 + self.table1 + '\n'*3 + self.table2
        pc.copy(self.planning_info)

        # show message box
        Messagebox.show_info('Planning information copied to clipboard!', title = 'Planning Information')

    
        

