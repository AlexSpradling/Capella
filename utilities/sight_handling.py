import sys
import os
import subprocess
import numpy as np
from skyfield.api import Angle
import pyperclip as pc
import re
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
import datetime as dt
import utilities.celestial_engine as celestial_engine
from utilities.sight_planning import SightSessionPlanning
from utilities.input_checking import InputChecking
from tabulate import tabulate

def save_sights_to_clipboard(instance, entries, sight_list_treeview):
    """
    Saves Sight Session and Sight info from Sight List trv and Session Data section, 
    formats it as a Markdown table and saves to clipboard.
    """
    session_array = []
    sight_array = []

    # Retrieve session data
    session = [ent.get() for ent in entries]
    session_array.append(session)

    # Retrieve sight data
    for record in sight_list_treeview.get_children():
        sight = sight_list_treeview.item(record, 'values')
        sight_array.append(sight)

    # Create Markdown tables with headers
    session_headers = ["DR Date", "DR Time", "DR L", "DR λ", "Course", "Speed"]
    sextant_headers = ["I.C.", "H.O.E", "Temp.", "Press."]
    fix_headers = ["Fix Date", "Fix Time"]
    sight_headers = ["Body", "Hs", "Date", "Time"]

    # Split session data into separate sections
    dr_data = session_array[0][:6]
    sextant_data = [session_array[0][6:10]]
    fix_data = [session_array[0][10:]]

    # Format each section with headers
    dr_copy = "### 1. Dead Reckoning Information\n" + tabulate([dr_data], headers=session_headers, tablefmt="github")
    sextant_copy = "### 2. Sextant Information\n" + tabulate(sextant_data, headers=sextant_headers, tablefmt="github")
    fix_copy = "### 3. Fix Date and Time Information\n" + tabulate(fix_data, headers=fix_headers, tablefmt="github")
    sight_copy = "### 4. Sights\n" + tabulate(sight_array, headers=sight_headers, tablefmt="github")

    # Combine all data
    copied_data = "\n\n".join([dr_copy, sextant_copy, fix_copy, sight_copy])
    pc.copy(copied_data)

    return dr_copy, sextant_copy, fix_copy, sight_copy

def load_sights_from_clipboard(instance, entries, sight_list_treeview):
    """
    Loads Sight Session DR info and Sights into the Session info Sights Treeview from the clipboard.
    """
    copied_text = pc.paste()

    try:
        # Split the copied text into sections
        sections = re.split(r'### \d\.\s.*\n', copied_text)
        sections = [section for section in sections if section.strip()]

        # Process DR information (section 0)
        dr_rows = sections[0].strip().split('\n')[2:]  # Skip headers and divider rows
        dr_data = [cell.strip() for cell in dr_rows[0].split('|') if cell.strip()]
        for j, value in enumerate(dr_data):
            entries[j].delete(0, 'end')
            entries[j].insert(0, value)

        # Process Sextant information and Fix Date and Time (sections 1 and 2)
        for i in range(1, 3):
            rows = sections[i].strip().split('\n')[2:]  # Skip headers and divider rows
            data = [cell.strip() for cell in rows[0].split('|') if cell.strip()]
            for j, value in enumerate(data):
                entry_index = 6 + (i - 1) * 4 + j  # Adjust index based on section
                entries[entry_index].delete(0, 'end')
                entries[entry_index].insert(0, value)

        # Clear Sight Entry treeview
        for i in sight_list_treeview.get_children():
            sight_list_treeview.delete(i)

        # Populate Sight Entry treeview (section 3)
        if len(sections) > 3:
            sights = sections[3].strip().split('\n')[2:]  # Skip headers and divider rows
            for i, sight in enumerate(sights):
                sight_data = [cell.strip() for cell in sight.split('|') if cell.strip()]
                sight_list_treeview.tag_configure('main', font=('Arial Bold', 12))
                sight_list_treeview.insert('', 'end', text='', iid=i, 
                                           values=sight_data, tags=('main',))
                instance.counter += 1   
    except:
        Messagebox.show_warning(title = 'Input Error', message = 'Data not in recognized format, check clipboard data.')
        return
    
    # check sight info for errors
    for i, record in enumerate(sight_list_treeview.get_children()):
        sight = sight_list_treeview.item(record, 'values')
        if not InputChecking.check_celestial_body(sight[0]):
            Messagebox.show_warning(title = f'Input Error Sight # {i+1}', message = 'Celestial Body Formatted Incorrectly, check entry in Sight Entry Treeview')
            return
        if not InputChecking.check_hs_format(sight[1]):
            Messagebox.show_warning(title = f'Input Error Sight # {i+1}', message = 'Hs Formatted Incorrectly, check entry in Sight Entry Treeview')
            return
        if not InputChecking.check_date_format(sight[2]):
            Messagebox.show_warning(title = f'Input Error Sight # {i+1}', message = 'Date Formatted Incorrectly, check entry in Sight Entry Treeview')
            return
        if not InputChecking.check_time_format(sight[3]):
            Messagebox.show_warning(title = f'Input Error Sight # {i+1}', message = 'Time Formatted Incorrectly, check entry in Sight Entry Treeview')
            return
        

def add_new_sight(instance, bodies_entry_box, entry_boxes, sight_list_treeview):
    
    """Adds a new row to the Sight Entry Treeview"""
    try:
        # Get values from entry boxes and add to Treeview
        values = [entry.get() for entry in entry_boxes]

        sight_list_treeview.tag_configure('main', font=('Arial Bold', 12))
        sight_list_treeview.insert('', 'end', text='', iid=instance.counter, values=values, tags=('main',))
        
        # Clear entry boxes
        for entry in entry_boxes:
            entry.delete(0, 'end')
        instance.counter += 1
        
    except Exception as e:
        print(f"Error adding new row to Sight Entry Treeview: {e}")
    
    # Set focus back to bodies autocomplete box
    bodies_entry_box.focus()

    return 

def delete_sight(sight_list_treeview):
    """Deletes selected row from Sight Entry Treeview"""
    selection = sight_list_treeview.selection()
    for record in selection:
        sight_list_treeview.delete(record)

def update_sight(entry_list, sight_list_treeview):
    """Updates entry fields in 'Sight Entry' section"""
    selected = sight_list_treeview.focus()
    selection = sight_list_treeview.item(selected, 'values')
    sight_list_treeview.tag_configure('main', font=('Arial Bold', 12))
    sight_list_treeview.item(selected, text='', values=(entry_list[0].get(), 
                                                        entry_list[1].get(), 
                                                        entry_list[2].get(), 
                                                        entry_list[3].get()), 
                                                        tags=('main', 0))


def open_sight_log(event=None):
    """Opens sight_log.txt file in the default text editor, in an OS-agnostic way."""
    # Define the path to the file
     # Get the directory where the current script (presumably __main__.py or similar) is located
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # go down one level to the root directory
    root_dir = os.path.dirname(current_dir)

    # go down one more level to the text_files directory
    text_files_dir = os.path.join(root_dir, 'text_files')

    # Define the path to the file
    file_path = os.path.join(text_files_dir, 'sight_log.txt')
   

    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # Open the file with the default application
    try:
        if sys.platform == 'win32':
            os.startfile(file_path)  # For Windows
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', file_path])  # For macOS
        else:
            subprocess.Popen(['xdg-open', file_path])  # For Linux
    except Exception as e:
        print(f"Error opening file: {e}")    

class UpdateAndAveraging:
    def __init__(self, treeview, ents):
        self.treeview = treeview
        self.ents = ents

    def print_element(self, event):
        """Click on a Sight in the Sight Field treeview and the Sight Entry input box values will change
        respectively """
        trv = event.widget
        selected = trv.focus()
        selection = trv.item(selected, 'values')

        for ent in self.ents:
            ent.delete(0, 'end')

        self.ents[0].insert(0, selection[0])
        self.ents[1].insert(0, selection[1])
        self.ents[2].insert(0, selection[2])
        self.ents[3].insert(0, selection[3])

        # Sight Averaging
        selection = trv.selection()
        datetimeList = []
        hsList = []
        for record in selection:
            # time averaging
            values = trv.item(record, 'values')
            year, month, day = values[2].split('-')
            hour, minute, second = values[3].split(':')
            sight_dt_obj = dt.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
            datetimeList.append(sight_dt_obj)
            avgTime = dt.datetime.strftime(dt.datetime.fromtimestamp(
                sum(map(dt.datetime.timestamp, datetimeList)) / len(datetimeList)), "%H:%M:%S")
            avgDate = dt.datetime.strftime(dt.datetime.fromtimestamp(
                sum(map(dt.datetime.timestamp, datetimeList)) / len(datetimeList)), "%Y-%m-%d")

            # hs averaging
            hs_deg, hs_min = values[1].split('-')
            hs = (float(hs_deg) + (float(hs_min) / 60))
            hs = Angle(degrees=(hs))
            hsList.append(hs.degrees)

            hs_avg = celestial_engine.Utilities.hmt_str_2(np.mean(hsList))

# make ent text red if more than one sight is selected

            if len(selection) >= 2:
                self.ents[1].config(foreground='cyan')
                self.ents[2].config(foreground='cyan')
                self.ents[3].config(foreground='cyan')
            else:
                self.ents[1].config(foreground='white')
                self.ents[2].config(foreground='white')
                self.ents[3].config(foreground='white')


            self.ents[1].delete(0, 'end')
            self.ents[2].delete(0, 'end')
            self.ents[3].delete(0, 'end')
            self.ents[1].insert(0, hs_avg)
            self.ents[2].insert(0, avgDate)
            self.ents[3].insert(0, avgTime)
            
            # if len(hsList) >= 2:
            #     avg_lbl.grid(row=1, column=2, padx=2, pady=3)
            #     avg_lbl_2.grid(row=3, column=2, padx=2, pady=3)
            # else:
            #     avg_lbl.grid_forget()
            #     avg_lbl_2.grid_forget()
