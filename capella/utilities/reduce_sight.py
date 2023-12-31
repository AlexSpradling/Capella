import numpy as np
from skyfield.api import Angle
from utilities.celestial_engine import Sight, SightSession, SightReduction, Utilities
import scipy.stats as stats
from ttkbootstrap.dialogs import Messagebox
from utilities.os_handler import get_os_type

# takes info from newpageone treeview, creates SightSession instance and Sight instances and then creates SightReduction instance
# adds Fix information to newpageone fix treeview


class CapellaSightReduction:
    error_flag = False

    def __init__(self, info_fields, treeviews, meter):
        self.sight_treeview = treeviews[0]
        self.fix_treeview = treeviews[1]
        self.info_fields = info_fields
        self.meter = meter

        self.get_fonts()
        self.delete_fix_treeview()
        self.create_sight_session()
        self.create_sights()
        self.create_sight_reduction()
        self.update_meter()
        self.add_fix_to_treeview()
        self.find_bad_sights()
        self.systematic_error_handling()

        self.cnav_data_array_wipe()

    def get_fonts(self):
        # get os
        if get_os_type() == "Windows":
            self.font = 15
        elif get_os_type() == "Unix" or get_os_type() == "Darwin":
            self.font = 12

    def delete_fix_treeview(self):
        # delete all items from fix treeview
        for i in self.fix_treeview.get_children():
            self.fix_treeview.delete(i)

    def create_sight_session(self):
        # get info from newpageone DR info fields
        self.session_instance = SightSession(
            ",".join(str(elem.get()) for elem in self.info_fields)
        )

        return self.session_instance

    def create_sights(
        self,
    ):
        # Iterate through treeview and create Sight instances using list comprehension
        self.sight_instances = [
            Sight(",".join(self.sight_treeview.item(i, "values")))
            for i in self.sight_treeview.get_children()
        ]

        return self.sight_instances

    def create_sight_reduction(self):
        # create SightReduction instance
        self.sight_reduction_instance = SightReduction(True)

        return self.sight_reduction_instance

    def add_fix_to_treeview(self):
        # tag configure
        self.fix_treeview.tag_configure("main", font=("Arial Bold", self.font))

        # add blank first row to treeview for spacing
        self.fix_treeview.insert(
            "", "end", text="", iid="blank", values="", tags=("main",)
        )

        # add fix to treeview
        for i in self.sight_reduction_instance.gui_position_table:
            self.fix_treeview.insert(
                "", "end", text="", iid=i, values=i, tags=("main",)
            )

    def update_meter(self):
        obj_fun_value = self.sight_reduction_instance.res.fun

        def calculate_confidence(obj_fun_value, max_obj_value=0.01):
            if obj_fun_value < 0:
                return 100  # Assuming negative values indicate perfect confidence
            elif obj_fun_value > max_obj_value:
                return 0  # No confidence if the value exceeds the maximum
            else:
                # Linear scaling of confidence
                return 100 * (1 - (obj_fun_value / max_obj_value))

        self.meter_value = calculate_confidence(obj_fun_value)
        self.meter.configure(value=int(self.meter_value))


    def find_bad_sights(self):
        """
        This method finds erroneous sights using z-scores and then asks the user if they want to delete the erroneous sight.
        """

        # get z-scores
        self.d_back = self.sight_reduction_instance.d_array
        self.d_forward = self.sight_reduction_instance.d_array_dr

        print(self.d_back)
        print(self.d_forward)

        # iterate through z-scores and highlight erroneous sights
        for idx, d in enumerate(self.sight_reduction_instance.d_array):
            # if z-score is highest in both directions
            if abs(self.d_back[idx]) > 100 and abs(self.d_forward[idx]) > 100 or abs(stats.zscore(self.d_back)[idx]) > 2.0:
                # get erroneous sight info
                erroneous_body = Sight.body_array[idx]
                # yyyy-mm-dd hh:mm:ss
                erroneous_sighttime = Sight.sight_times[idx].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                # create tag
                self.sight_treeview.tag_configure(
                    "red", foreground="red", font=("Arial Bold", self.font)
                )

                # highlight erroneous sight
                self.sight_treeview.item(idx, tags=("red",))

                # ask user if they want to delete erroneous sight
                erroneous_answer = Messagebox.show_question(
                    f"{erroneous_body} observation at {erroneous_sighttime} is likely erroneous.\n\n Correct the observation or remove from Sight List, otherwise consider fix and analysis unreliable. \
                    \n\n Would you like to delete this observation?"
                )

                # if yes delete erroneous sight
                if erroneous_answer == "Yes":
                    error_flag = True
                    # set selection
                    self.sight_treeview.selection_set(idx)

                    # delete erroneous sight
                    for i in self.sight_treeview.selection():
                        self.sight_treeview.delete(i)
                    error_flag = False

                    # wipe data arrays and run CapellaSightReduction again
                    self.cnav_data_array_wipe()
                    CapellaSightReduction(self.info_fields, [self.sight_treeview, self.fix_treeview], self.meter)
        
    
    def systematic_error_handling(self):
        """
        This method finds the systematic error and asks the user if they want to remove it.
        """

        self.count = 0
        # self.systematic_error = np.mean(self.sight_reduction_instance.d_array)

        # make systematic_error the trimmed mean of d_array
        self.systematic_error = stats.trim_mean(
            self.sight_reduction_instance.d_array, 0.1
        )

        message = f"Capella found a Constant Error (Uncorrected Index Error + Personal Error) of: {np.round(self.systematic_error, 2)}'.\
        \n\n\n Would you like to remove this error? "

        if abs(self.systematic_error) >= 0.25:
            error_flag = True
            error_message = Messagebox.show_question(
                message,
                "Systematic Error",
            )
            if self.systematic_error < 0:
                self.systematic_error = abs(self.systematic_error / 60)
            else:
                self.systematic_error = self.systematic_error / 60 * -1

            if error_message == "Yes" and self.systematic_error != 0:
                for i in self.sight_treeview.get_children():
                    body = self.sight_treeview.item(i, "values")[0]
                    hs = self.sight_treeview.item(i, "values")[1]
                    date = self.sight_treeview.item(i, "values")[2]
                    time = self.sight_treeview.item(i, "values")[3]
                    hs_deg, hs_min = hs.split("-")
                    hs = float(hs_deg) + float(hs_min) / 60
                    hs = Angle(degrees=hs)
                    hs = Utilities.hmt_str_2(hs.degrees + self.systematic_error)
                    self.sight_treeview.delete(i)
                    self.sight_treeview.insert(
                        "",
                        "end",
                        text="",
                        iid=i,
                        values=(body, hs, date, time),
                        tags=("main",),
                    )

                # wipe data arrays and run CapellaSightReduction again
                self.cnav_data_array_wipe()

                # recursively run CapellaSightReduction
                CapellaSightReduction(
                    self.info_fields,
                    [self.sight_treeview, self.fix_treeview],
                    self.meter,
                )
                self.count += 1
                error_flag = False

        else:
            return

    def cnav_data_array_wipe(self):
        # Sight_session
        SightSession.num_of_sights = 0
        SightSession.dr_details = []

        # Sight
        Sight.data_table = []
        Sight.sight_times = []
        Sight.num_of_sights = 0
        Sight.body_array = []
        Sight.sight_az_array = []
        Sight.sight_times = []
        Sight.computedlong = []
        Sight.computedlat = []
        Sight.intercept_array = []
        Sight.ho_array = []
        Sight.dec_array_lop = []
        Sight.gha_array_lop = []
        Sight.hc_array = []
        Sight.gha_dec_array = []
        Sight.test_array_ho = []
        Sight.ho_vec_array = []
        Sight.test_array_gha = []

        # Sight_Reduction

        SightReduction.gui_position_table = []
        SightReduction.test_array
        SightReduction.final_position_array = []
        SightReduction.stats_table_2 = []
        SightReduction.latx_lists = []
        SightReduction.longx_lists = []

        SightReduction.ho_array_rfix = []
        SightReduction.time_delta_array = []
        SightReduction.sight_anl_table = []
        SightReduction.final_ho_array = []
        SightReduction.pos_array_lop_lon = []
        SightReduction.pos_array_lop_lat = []
        SightReduction.d_array = []
        SightReduction.ho_corrections_array = []
        SightReduction.longitude_array = []
        SightReduction.latitude_array = []
        SightReduction.hc_timeofsight = []
        SightReduction.sight_analysis_lat_time_of_sight = []
        SightReduction.sight_analysis_long_time_of_sight = []
        SightReduction.sight_analysis_lat_minus_one = []
        SightReduction.sight_analysis_long_minus_one = []
        SightReduction.sight_analysis_lat_plus_one = []
        SightReduction.sight_analysis_long_plus_one = []
        SightReduction.hc_minusone = []
        SightReduction.hc_plusone = []
        SightReduction.drsight_analysis_lat_time_of_sight = []
        SightReduction.drsight_analysis_long_time_of_sight = []
        SightReduction.drsight_analysis_lat_minus_one = []
        SightReduction.drsight_analysis_long_minus_one = []
        SightReduction.drsight_analysis_lat_plus_one = []
        SightReduction.drsight_analysis_long_plus_one = []
        SightReduction.drhc_timeofsight = []
        SightReduction.drhc_minusone = []
        SightReduction.drhc_plusone = []
        SightReduction.d_array = []
        SightReduction.d_array_dr = []
        SightReduction.position_array_l = []
