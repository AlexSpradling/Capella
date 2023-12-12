import sys
import os
import subprocess
import numpy as np
from skyfield.api import Angle
import pyperclip as pc
import re
from ttkbootstrap.dialogs import Messagebox
import datetime as dt
import capella.utilities.celestial_engine as celestial_engine
from capella.utilities.sight_planning import SightSessionPlanning
from capella.utilities.input_checking import InputChecking
from tabulate import tabulate

def save_sights_to_clipboard(instance, entries, sight_list_treeview):
    """
     Saves Sight Session and Sight info from Sight List trv and Session Data section, formats it as a Markdown table and saves to clipboard.
     """
    session_array = []
    sight_array = []

    session_array = []
    sight_array = []
    session = [ent.get() for ent in entries]
    session_array.append(session)
    for record in sight_list_treeview.get_children():
        sight = sight_list_treeview.item(record, 'values')
        sight_array.append(sight)
    # create Markdown table
    session_headers = ["DR Date", "DR Time", "DR L", "DR λ", "Course", "Speed", "I.C.", "H.O.E", "Temp.",
                        "Press.", "Fix Date", "Fix Time"]
    session_copy = tabulate(session_array, headers=session_headers, tablefmt="github")
    sight_headers = ["Body", "Hs", "Date", "Time"]

    sight_copy = tabulate(sight_array, headers=sight_headers, tablefmt="github")

    copied_data = session_copy + "\n \n" + sight_copy
    pc.copy(copied_data)

    return session_copy, sight_copy


def load_sights_from_clipboard(instance, entries, sight_list_treeview):
    """
    Loads Sight Session DR info and Sights into the Session info Sights Treeview from the clipboard.

    Parameters
    ----------
    entries : list
        List text entry widgets from the Session info frame.
    sight_list_treeview : ttk.Treeview
        Treeview widget from the Sight data frame.
    """
    copied_text = pc.paste()
    print(copied_text)
    
    try:
        # raw copied data
        copied1 = pc.paste()
        copied1 = re.sub(r" ", '', copied1)
        
        # split into session data chunk
        split = str(copied1.split()[2]).strip("|")
        length = len(split)

        # further slice session chunk and populate Session info text fields
        for i, value in enumerate(split.split('|')[:12]):
            entries[i].delete(0, 'end')
            entries[i].insert(0, value)

        # clear Sight Entry treeview
        for i in sight_list_treeview.get_children():
            sight_list_treeview.delete(i)

        # populate Sight Entry treeview
        for i in range(length):
            try:
                sight_list_treeview.tag_configure('main', font=('Arial Bold', 10))
                sight_list_treeview.insert('', 'end', text='', iid=i, 
                    values=(copied1.split()[i + 5]).strip("|").split('|'), tags=('main',))
                instance.counter += 1
            except:
                pass 
         

    # if info is formatted incorrectly send error message
    except:
        print('Error message', file = sys.stderr)
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

        sight_list_treeview.tag_configure('main', font=('Arial Bold', 10))
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
    sight_list_treeview.tag_configure('main', font=('Arial Bold', 10))
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
   
    print(file_path)

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
