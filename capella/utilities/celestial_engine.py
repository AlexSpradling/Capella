import os
os.system('color')
from skyfield.api import load, Angle, Star, Topos, utc, wgs84
from skyfield import almanac
from skyfield.data import hipparcos
with load.open(hipparcos.URL) as f:
    df = hipparcos.load_dataframe(f)
import re, datetime as dt
from datetime import timezone, timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker
import matplotlib.dates as mdates

from matplotlib.patches import Ellipse
from tabulate import tabulate
import scipy.optimize as optimize
from capella.utilities.utility_funcs import Utilities
from capella.utilities.dead_reckoning import DRCalc

planets = load('de421.bsp')
ts = load.timescale()

class SightSession():
    """
    The Sight_session class takes all, of the pre-sight information that is relevant for the reduction process and
    passes it down to each Sight class. The idea is to represent an actual Sight-taking process. The Sight_session class
    gathers values that are only needed once, such as course or speed or index error.

    Parameters
    ----------
    date : np.array
        Covariance matrix from L-BFGS-B function
    time : tuple
        x, y position for center of ellipse
    dr_lat : int
        number of standard deviations.
    """
    dr_details = []
    num_of_sights = 0

    def __init__(self, data):
        # date, time,dr_lat,dr_long,course,speed,i_e,h_o_e,temp,pressure
        date, time, dr_lat, dr_long, course, speed, i_e, h_o_e, temp, pressure, fixdate, fixtime = data.split(',')

        self.date = date
        self.time = time
        self.course = Angle(degrees=(float(course)))
        self.speed = float(speed)
        deg, minutes, direction = dr_lat.split('-')
        self.dr_lat = (float(deg) + (float(minutes) / 60)) * (-1 if direction in 'S' else 1)
        deg, minutes, direction = dr_long.split('-')
        self.dr_long = (float(deg) + (float(minutes) / 60)) * (-1 if direction in 'W' else 1)
        self.i_e = Angle(degrees=(float(i_e) / 60))
        self.h_o_e = float(h_o_e)
        self.temp = float(temp)
        self.pressure = float(pressure)

        year, month, day = date.split('-')
        hour, minute, second = time.split(':')
        zd = int()
        tz = timezone(timedelta(hours=zd))
        self.datetime = dt.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), tzinfo=tz)

        fix_year, fix_month, fix_day = fixdate.split('-')
        fixhr, fixmin, fixsec = fixtime.split(':')
        self.fixtime = dt.datetime(int(fix_year), int(fix_month), int(fix_day), int(fixhr), int(fixmin), int(fixsec),
                                   tzinfo=tz)
        SightSession.dr_details.append(
            [self.datetime, self.dr_lat, self.dr_long, self.course, self.speed, self.i_e, self.h_o_e, self.temp,
             self.pressure, self.fixtime])
        return

class Sight(SightSession):
    """
    The Sight class represents each individual sextant sight. It has a data/time a sextant Hs and a Body. Each Sight class
    instance is passed to the Sight_Reduction class.
    """
    num_of_sights = 0
    sight_times = []
    ho_array = []
    ho_vec_array = []
    sight_az_array = []
    gha_array_lop = []
    dec_array_lop = []
    body_array = []
    test_array_gha = []
    test_array_ho = []
    data_table = []

    computedlat = []
    computedlong = []
    hc_array = []
    intercept_array = []

    named_star_dict = {
        'Acamar': 13847, 'Achernar': 7588, 'Acrux': 60718, 'Adhara': 33579, 'Aldebaran': 21421, 'Algol': 14576,
        'Alioth': 62956,
        'Alkaid': 67301, 'Alnair': 109268, 'Alnilam': 26311, 'Alphard': 46390, 'Alphecca': 76267, 'Alpheratz': 677,
        'Altair': 97649,
        'Ankaa': 2081, 'Antares': 80763, 'Arcturus': 69673, 'Atria': 82273, 'Avior': 41037, 'Becrux': 62434,
        'Bellatrix': 25336,
        'Betelgeuse': 27989, 'Canopus': 30438, 'Capella': 24608, 'Deneb': 102098, 'Denebola': 57632, 'Diphda': 3419,
        'Dubhe': 54061,
        'Elnath': 25428, 'Enif': 107315, 'Eltanin': 87833, 'Fomalhaut': 113368, 'Gacrux': 61084, 'Gienah': 102488,
        'Hadar': 68702, 'Hamal': 9884, 'Kaus Australis': 90185, 'Kochab': 72607, 'Markab': 113963, 'Menkent': 68933,
        'Merak': 53910,
        'Miaplacidus': 45238, 'Mirach': 5447, 'Mirfak': 15863, 'Nunki': 92855, 'Peacock': 100751, 'Polaris': 11767,
        'Pollux': 37826,
        'Procyon': 37279, 'Rasalhague': 86032, 'Regulus': 49669, 'Rigel': 24436, 'Rigel Kent': 71683,
        'RigilKentaurus': 71683,
        'Sabik': 84012, 'Schedar': 3179, 'Shaula': 85927, 'Sirius': 32349, 'Spica': 65474, 'Suhail': 44816,
        'Vega': 91262,
        'Zubenelgenubi': 72622,
    }

    def __init__(self, data):

        body, hs, date, time = data.split(',')
        self.body = body
        self.date = date
        self.time = time
        hs_deg, hs_min = hs.split('-')
        hs = (float(hs_deg) + (float(hs_min) / 60))
        self.hs = Angle(degrees=(hs))
        year, month, day = date.split('-')
        hour, minute, second = time.split(':')
        self.datetime = dt.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), tzinfo=utc)
        self.t = ts.utc(self.datetime)
        Sight.num_of_sights += 1
        # plot.session.num_of_sights += 1

        self.get_dr_time_delta()
        self.get_dr_details()
        self.get_sight_dr_positions()

        self.compute_gha_dec()
        self.dip_correction()
        self.index_correction()
        self.ha_calc()
        self.get_HP()
        self.parallax_altitude_correction()
        self.semi_diameter_correction()
        self.refraction()
        self.ho_constructor()
        self.hc_constructor()
        self.intercept()

        self.sight_data = [f'{Sight.num_of_sights - 1}',
                           f'{self.body.upper()}',
                           Utilities.print_position(self.computed_lat, latitude=True),
                           Utilities.print_position(self.computed_long, latitude=False),
                           f'{self.time}',
                           f'{Utilities.hmt_str(self.GHA.degrees)}',
                           f'{Utilities.hmt_str(self.DEC.degrees)}',
                           f'{round(self.AZ.degrees, )}',
                           f'{Utilities.hmt_str(self.ho.degrees)}',
                           f'{Utilities.hmt_str(self.hc.degrees)}',
                           f'{format(self.int, ".1f")}'
                           ]

        Sight.data_table.append(self.sight_data)
        Sight.sight_times.append(self.datetime)
        Sight.body_array.append(self.body)

        self.array_creation()

        Sight.ho_array.append(self.ho_array)
        Sight.sight_az_array.append(self.AZ)

        return

    def get_dr_time_delta(self):
        """Computes the time delta in seconds between the DR time and the time of the Sight"""
        self.dr_time = SightSession.dr_details[0][0]
        self.sighttime = self.datetime
        self.drtimedelta = dt.timedelta.total_seconds(self.sighttime - self.dr_time)

        return

    def get_dr_details(self):
        """Fetches DR Lat, Long, Course, Speed from Sight_session class dr_details list"""
        self.dr_lat = SightSession.dr_details[0][1]
        self.dr_long = SightSession.dr_details[0][2]
        self.course = SightSession.dr_details[0][3]
        self.speed = SightSession.dr_details[0][4]

        return

    def get_sight_dr_positions(self):
        """Uses get_dr_time_delta and get_dr_details functions to provide information to dr_calc class"""
        lat = self.dr_lat
        long = self.dr_long
        course = self.course
        speed = self.speed
        timed = self.drtimedelta
        self.computed_lat = DRCalc(lat, long, timed, course.degrees, speed).drlatfwds
        self.computed_long = DRCalc(lat, long, timed, course.degrees, speed).drlongfwds
        Sight.computedlat.append(self.computed_lat)
        Sight.computedlong.append(self.computed_long)

        return

    def compute_gha_dec(self):
        """Functionally identical to Get_GHA_DEC function in utilities, just called every time a Sight Object
         is initialized"""
        body = self.body
        if body == 'SunLL' or body == 'SunUL':
            celestial_body = planets['Sun']
        elif body == 'MoonLL' or body == 'MoonUL':
            celestial_body = planets['Moon']
        elif body == 'Mars':
            celestial_body = planets['Mars']
        elif body == 'Venus':
            celestial_body = planets['Venus']
        elif body == 'Jupiter':
            celestial_body = planets['Jupiter Barycenter']
        elif body == 'Saturn':
            celestial_body = planets['Saturn Barycenter']
        elif body == 'Uranus':
            celestial_body = planets['Uranus Barycenter']
        elif body == 'Mercury':
            celestial_body = planets['Mercury']
        else:
            which_star = body
            hid = Sight.named_star_dict.get(which_star)
            celestial_body = Star.from_dataframe(df.loc[hid])
        obs = planets['Earth']
        # datetime object of sight
        dt = self.t.utc_datetime()
        # time delta between DR dateime object and Sight datetimeobject

        position = obs + Topos(latitude_degrees=(self.computed_lat), longitude_degrees=(self.computed_long))

        astro = position.at(self.t).observe(celestial_body)
        app = astro.apparent()

        astrometric = obs.at(self.t).observe(celestial_body)
        apparent = obs.at(self.t).observe(celestial_body).apparent()
        alt, az, distance = app.altaz()
        ra, dec, distance, = apparent.radec(epoch='date')

        ghaa = Angle(degrees=(self.t.gast) * 15)
        gha = Angle(degrees=((self.t.gast - ra.hours) * 15 % 360 - 0))
        self.GHA = gha
        self.DEC = dec
        self.ALT = alt
        self.AZ = az
        self.DIST = distance
        self.ghaa = ghaa

        return

    def dip_correction(self):
        """Uses height of eye in feet provided in Sight_session.dr_details to compute dip correction"""
        dip_corr = Angle(degrees=(-1 * (.97 * np.sqrt(SightSession.dr_details[0][6])) / 60))
        self.dip_corr = dip_corr

        return

    def index_correction(self):
        """Uses user provided index error in arc minutes provided in Sight_session.dr_details to compute dip
        correction """
        index_corr = SightSession.dr_details[0][5]
        self.index_corr = index_corr

        return

    def ha_calc(self):
        """Calculates Ha in degrees from hs, dip and index correction functions"""
        ha = Angle(degrees=(self.hs.degrees + self.dip_corr.degrees + self.index_corr.degrees))
        self.ha = ha

        return

    def get_HP(self):
        """Calculates Horizontal Parallax in degrees for Sun, Moon. If Venus, Saturn, Mars or Jupiter are provided,
        it uses the same formula to calculate HP as the difference is not noticeable for celestial navigation"""
        body = self.body
        if body == 'SunLL' or body == 'SunUL':
            self.hp_degrees = Angle(degrees=(0.0024))
        elif body == 'MoonLL' or body == 'MoonUL':
            distance_rad = np.deg2rad(self.DIST.km)
            hp_numerator = np.deg2rad(6378.14)
            hp_rad = np.arcsin(hp_numerator / distance_rad)
            hp_degrees = np.rad2deg(hp_rad)
            self.hp_degrees = Angle(degrees=hp_degrees)
        elif body == 'Venus' or body == 'Saturn' or body == 'Mars' or body == 'Jupiter':
            distance = self.DIST.km
            self.hp_degrees = Angle(degrees=(1.315385814 * 10 ** 9 / distance) / 3600)

        else:
            self.hp_degrees = Angle(degrees=(0))
        return

    def parallax_altitude_correction(self):
        """Calculates the parallax altitude correction in degrees using the get_HP function"""
        body = self.body

        if body == 'Venus' or body == 'Mars':
            parallax_corr = Angle(degrees=(self.hp_degrees.degrees * np.cos(self.ha.radians) * (
                    1 - (np.sin(np.deg2rad(SightSession.dr_details[0][1])) ** 2.0) / 297.0)))
            self.parallax_corr = parallax_corr

        elif body == 'SunLL' or body == 'SunUL':
            parallax_corr = Angle(degrees=(self.hp_degrees.degrees * np.cos(self.ha.radians) *
                                           (1 - (np.sin(np.deg2rad(SightSession.dr_details[0][1])) ** 2.0) / 297.0)))
            self.parallax_corr = parallax_corr

        elif body == 'MoonLL' or body == 'MoonUL':

            OB = Angle(degrees=(-0.0017 * np.cos(self.ha.radians)))
            parallax_corr = Angle(degrees=(self.hp_degrees.degrees * np.cos(self.ha.radians) *
                                           (1 - (np.sin(np.deg2rad(SightSession.dr_details[0][1])) ** 2.0) / 297.0)))

            self.parallax_corr = Angle(degrees=parallax_corr.degrees + OB.degrees)

        else:
            parallax_corr = Angle(degrees=(0))
            self.parallax_corr = parallax_corr

        return

    def semi_diameter_correction(self):
        """Calculates semi-diameter correction in degrees for Sun or Moon"""
        body = self.body

        if body == 'SunLL' or body == 'SunUL':
            sds = Angle(degrees=((15.9938 / self.DIST.au) / 60))
            if body == 'SunLL':
                self.sd_corr = Angle(degrees=(sds.degrees))
            else:
                self.sd_corr = Angle(degrees=(-1 * sds.degrees))

        elif body == 'MoonLL' or body == 'MoonUL':
            sdm = Angle(degrees=(.272476 * (self.hp_degrees.degrees)))
            sdm_tc = Angle(degrees=(sdm.degrees * (1 + np.sin(self.ALT.radians) / 60.27)))
            if body == 'MoonLL':
                self.sd_corr = Angle(degrees=(sdm_tc.degrees))
            else:
                self.sd_corr = Angle(degrees=(-1 * sdm_tc.degrees))
        else:
            self.sd_corr = Angle(degrees=(0))

        return

    def refraction(self):
        """Calculates refraction correction in degrees for celestial object"""
        pmb = SightSession.dr_details[0][8]
        TdegC = SightSession.dr_details[0][7]
        f = 0.28 * pmb / (TdegC + 273.0)
        ro = -1 * ((0.97127 / np.tan(self.ha.radians)) - (0.00137 / (np.tan(self.ha.radians)) ** 3)) / 60
        self.ref = Angle(degrees=(ro * f))

        return

    def ho_constructor(self):
        """Calculates Ho in degrees using the ha_calc, refraction, semi_diameter_correction and
        parallax_altitude_correction functions """
        ho = Angle(degrees=(self.ha.degrees + self.ref.degrees + self.sd_corr.degrees + self.parallax_corr.degrees))
        self.ho = ho
        return

    def hc_constructor(self):
        """Calculates Hc in degrees using lat and long provided by the get_sight_dr_positions function """
        lha = Angle(degrees=(self.computed_long + self.GHA.degrees) % 360)
        lat = Angle(degrees=self.computed_lat)

        self.hc = Angle(radians=(np.arcsin(
            np.sin(lat.radians) * np.sin(self.DEC.radians) + np.cos(lat.radians) * np.cos(self.DEC.radians) * np.cos(
                lha.radians))))

        return

    def intercept(self):
        """Calculates the Marc St.Hillaire intercept in minutes using the ho_constructor and hc_constructor methods.
        This is for the navigators reference only and isn't used by the internal position calculation. """
        intercept = (self.ho.degrees) - self.hc.degrees
        self.int = float(intercept * 60)
        Sight.intercept_array.append(intercept)

        return

    def array_creation(self):
        """appends to Sight.ho_array, Sight.gha_array_lop and Sight.dec_array_lop"""
        ho_array = np.array([(self.ho.degrees)])
        self.ho_array = ho_array
        Sight.gha_array_lop.append(self.GHA.radians)
        Sight.dec_array_lop.append(self.DEC.radians)

        return


class SightReduction(Sight):
    """ The main Sight Reduction algorithm and plotting algorithms live here. SightReduction() doesn't fire unless
    it is instantiated as True, and will not work unless the required arrays in Sight() and SightSession() are
    filled. For multiple Sight Reductions (essential for the iterative recomputations), the arrays need to be reset
    to empty every time, this happens in main.py currently.

    Potential Improvements:
    1. Remove plotting functionality entirely
    2. Reset arrays internal to cnav.py
    """
    time_delta_array = []
    ho_corrections_array = []
    final_ho_array = []
    position_array_l = []
    position_array_lon = []
    latx_lists = []
    longx_lists = []
    ho_array_rfix = []
    pos_array_lop_lon = []
    pos_array_lop_lat = []
    final_position_array = []
    sight_anl_table = []
    gui_position_table = []

    def __init__(self, reduction):
        self.reduction = reduction
        self.last_time = None
        self.last_time_sort()
        self.ho_correction()
        self.final_ho_sr()
        self.vector_reduction()
        self.sight_analysis()
        # self.error_trapping()

        self.bx_method()
        self.scatter_plot_analyzer()
        self.lop_plot()

    def last_time_sort(self):
        """Computes the time delta in total seconds between the user provided time of fix and the time of each sight
        object, appends to Sight_Reduction.time_delta_array
        """
        fix_time = SightSession.dr_details[0][9]
        for i in range(Sight.num_of_sights):
            SightReduction.time_delta_array.append(dt.timedelta.total_seconds(fix_time - Sight.sight_times[i]))
        return

    def ho_correction(self):
        """advances/retards the sight lop by changing the Ho value using DR course/speed information.

        Parameters
        ----------
        Sight_session.dr_details[0][4] : float
            DR Speed information from Sight_session object
        Sight_session.dr_details[0][3]: float
            DR Course information in radians
        Sight.sight_az_array : float
            Angle object computed in Sight.Get_GHADEC

        """
        for i in range(Sight.num_of_sights):
            SightReduction.ho_corrections_array.append((SightSession.dr_details[0][4]
                                                        * (SightReduction.time_delta_array[i] / 3600)) / 60
                                                       * np.cos(Sight.sight_az_array[i].radians
                                                                 - SightSession.dr_details[0][3].radians))

        return

    def final_ho_sr(self):
        """Sums Sight.ho_array and Sight_Reduction.ho_corrections_array to create Sight_Reduction.ho_array_rfix,
        an array of Ho's corrected for the movement of the vessel to compute a running fix. """
        for i in range(Sight.num_of_sights):
            SightReduction.ho_array_rfix.append(
                np.deg2rad(Sight.ho_array[i] + SightReduction.ho_corrections_array[i]))
        return

    latitude_array = []
    longitude_array = []
    test_array = []

    def obj_function(self, params):
        """Objective Function to be minimized."""
        int_sum = []
        lat, long = params
        for i in range(len(Sight.body_array)):
            gha = Sight.gha_array_lop[i]
            dec = Sight.dec_array_lop[i]
            lha = (long + np.rad2deg(gha)) % 360
            hc = np.arcsin(np.sin(np.deg2rad(lat)) * np.sin(dec) + 
                           np.cos(np.deg2rad(lat)) * np.cos(dec) * np.cos(np.deg2rad(lha)))
            ho = SightReduction.ho_array_rfix[i]
            intercept = ho - hc
            int_sum.append(intercept ** 2)
        return np.sqrt(np.sum(int_sum) / Sight.num_of_sights)

    def calculate_initial_guess(self):
        """Calculate initial guess for optimization."""
        dr_details = SightSession.dr_details[0]
        dr_calc_lat = DRCalc(dr_details[1], dr_details[2],
                             timedelta.total_seconds(dr_details[9] - dr_details[0]),
                             dr_details[3].degrees, dr_details[4])
        dr_lat = dr_calc_lat.drlatfwds  # Assuming drlatfwds returns forward latitude
        dr_long = dr_calc_lat.drlongfwds  # Assuming drlongfwds returns forward longitude
        return dr_lat, dr_long

    def vector_reduction(self):
        """Computes fix using optimization given the Sight and SightSession information."""
        self.dr_lat, self.dr_long = self.calculate_initial_guess()

        # Use genetic algorithm for optimization
        self.res = optimize.differential_evolution(self.obj_function, bounds=[(0, 90), (-180, 180)])

        # Process optimization results
        self.process_optimization_results()

        # Update computed values and format for display
        self.update_computed_values()

        # Append results to class arrays
        self.append_results()

    def process_optimization_results(self):
        """Process the results from the optimization."""
        # Create table for scipy optimization results
        headers = ["Success", "Iterations", "Func. Value"]
        res_info = [[self.res.success, self.res.nit, self.res.fun]]
        self.res_info_str = tabulate(res_info, headers=headers)

        # Calculate errors from inverse Hessian
        try:
            hess_inv_diag = np.sqrt(np.diag(self.res.hess_inv.todense()))
            self.latitude_error, self.longitude_error = hess_inv_diag
        except Exception as e:
            print(f"Error processing Hessian: {e}")
            self.latitude_error = self.longitude_error = None

    def update_computed_values(self):
        """Update computed values for latitude and longitude."""
        self.fit_latitude = Angle(degrees=(self.res.x[0]))
        self.fit_longitude = Angle(degrees=(self.normalize_longitude(self.res.x[1])))

    def normalize_longitude(self, longitude):
        """Normalize longitude to be within -180 to 180 degrees."""
        if longitude > 180:
            return longitude - 360
        elif longitude < -180:
            return longitude + 360
        return longitude

    def append_results(self):
        """Append results to class arrays."""
        lat_sign = 'N' if self.fit_latitude.degrees >= 0 else 'S'
        long_sign = 'E' if self.fit_longitude.degrees >= 0 else 'W'

        self.print_latitude = self.fit_latitude if lat_sign == 'N' else Angle(degrees=abs(self.fit_latitude.degrees))
        self.print_longitude = self.fit_longitude if long_sign == 'E' else Angle(degrees=abs(self.fit_longitude.degrees))

        self.final_l_string = f'{Utilities.hmt_str(self.print_latitude.degrees)} {lat_sign}'
        self.final_lon_string = f'{Utilities.hmt_str(self.print_longitude.degrees)} {long_sign}'

        SightReduction.position_array_l.append(self.final_l_string)
        SightReduction.position_array_lon.append(self.final_lon_string)
        SightReduction.pos_array_lop_lat.append(self.fit_latitude.degrees)
        SightReduction.pos_array_lop_lon.append(self.fit_longitude.degrees)

        self.fixtime = SightSession.dr_details[0][9]

    sight_analysis_lat_time_of_sight = []
    sight_analysis_long_time_of_sight = []
    sight_analysis_lat_plus_one = []
    sight_analysis_long_plus_one = []
    sight_analysis_lat_minus_one = []
    sight_analysis_long_minus_one = []
    hc_timeofsight = []
    hc_plusone = []
    hc_minusone = []
    stats_table_2 = []

    ####

    drsight_analysis_lat_time_of_sight = []
    drsight_analysis_long_time_of_sight = []
    drsight_analysis_lat_plus_one = []
    drsight_analysis_long_plus_one = []
    drsight_analysis_lat_minus_one = []
    drsight_analysis_long_minus_one = []
    drhc_timeofsight = []
    drhc_plusone = []
    drhc_minusone = []

    def calculate_position(self, lat, long, time_delta, course, speed):
        dr_calc = DRCalc(lat, long, time_delta, course, speed)
        return dr_calc.drlatbackwards, dr_calc.drlongbackwards

    def calculate_heavenly_body_info(self, body, datetime, lat, long):
        ephem = Utilities.get_gha_dec(body, datetime, lat, long)
        gha, dec = ephem[0], ephem[1]
        lat_hc = Angle(degrees=lat)
        long_hc = Angle(degrees=long)
        lha = Angle(degrees=(gha.degrees + long_hc.degrees))
        hc = np.arcsin((np.sin(lat_hc.radians) * np.sin(dec.radians)) + 
                       (np.cos(lat_hc.radians) * np.cos(dec.radians) * np.cos(lha.radians)))
        return np.rad2deg(hc)

    def sight_analysis(self):
        lat = float(self.fit_latitude.degrees)
        long = float(self.fit_longitude.degrees)
        course = SightSession.dr_details[0][3].degrees
        speed = SightSession.dr_details[0][4]

        for i in range(Sight.num_of_sights):
            time_delta = self.time_delta_array[i]
            sight_time = Sight.sight_times[i]
            body = Sight.body_array[i]

            # Calculate positions for exact, +1 minute, and -1 minute times
            lat_time_of_sight, long_time_of_sight = self.calculate_position(lat, long, time_delta, course, speed)
            lat_plus_one, long_plus_one = self.calculate_position(lat, long, time_delta + 60, course, speed)
            lat_minus_one, long_minus_one = self.calculate_position(lat, long, time_delta - 60, course, speed)

            # Store calculated positions
            self.sight_analysis_lat_time_of_sight.append(lat_time_of_sight)
            self.sight_analysis_long_time_of_sight.append(long_time_of_sight)
            self.sight_analysis_lat_plus_one.append(lat_plus_one)
            self.sight_analysis_long_plus_one.append(long_plus_one)
            self.sight_analysis_lat_minus_one.append(lat_minus_one)
            self.sight_analysis_long_minus_one.append(long_minus_one)

            # Calculate and store heavenly body information
            self.datetime = sight_time
            self.hc_timeofsight.append(self.calculate_heavenly_body_info(body, self.datetime, lat_time_of_sight, long_time_of_sight))
            self.datetime = sight_time + dt.timedelta(seconds=60)
            self.hc_plusone.append(self.calculate_heavenly_body_info(body, self.datetime, lat_plus_one, long_plus_one))
            self.datetime = sight_time - dt.timedelta(seconds=60)
            self.hc_minusone.append(self.calculate_heavenly_body_info(body, self.datetime, lat_minus_one, long_minus_one))

    d_array = []

    
    def y_fmt(self, y, x):
        """Format matplotlib y-value ("dd°mm')"""
        return Utilities.hmt_str(y)

    def datetime_to_float(self, d):
        """Convert datetime to timestamp"""
        return d.timestamp()

    def setup_subplot(self, num_of_sights, index):
        """Setup a subplot based on the number of sights and current index"""
        if num_of_sights % 2 == 0:
            gs = gridspec.GridSpec(2, num_of_sights // 2)
        elif num_of_sights < 6:
            gs = gridspec.GridSpec(2, 3)
        elif 6 < num_of_sights < 9:
            gs = gridspec.GridSpec(2, 4)
        else:
            gs = gridspec.GridSpec(4, 4)

        ax = plt.subplot(gs[index])
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(self.y_fmt))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))
        ax.set_facecolor('#212946')
        ax.grid(color='#2A3459')
        ax.tick_params(axis='x', rotation=-45, labelsize=6)
        ax.tick_params(axis='y', rotation=45, labelsize=6)
        return ax

    def scatter_plot_analyzer(self):
        """Matplotlib plotting function for sight_analysis."""
        d_dict = {}
        top_unique_indexes = []
        plt.style.use('dark_background')
        plt.subplots(figsize=[7, 7])
        plt.figure(1)
        plt.clf()

        for i in range(Sight.num_of_sights):
            one = SightReduction.hc_plusone[i]
            two = SightReduction.hc_minusone[i]
            three = Sight.ho_array[i]
            four = SightReduction.hc_timeofsight[i]

            time1 = Sight.sight_times[i]
            time_before = time1 + dt.timedelta(seconds=60)
            time_after = time1 - dt.timedelta(seconds=60)

            x = np.array([time_before, time1, time_after])
            y = np.array([two, four, one])

            ax = self.setup_subplot(Sight.num_of_sights, i)

            ax.plot(x, y)
            ax.scatter(time1, three, color='red')

            p1 = np.array([self.datetime_to_float(time_after), one], dtype=object)
            p2 = np.array([self.datetime_to_float(time_before), two], dtype=object)
            p3 = np.array([self.datetime_to_float(time1), three], dtype=object)
            p4 = np.array([self.datetime_to_float(time1), four], dtype=object)

            d = float((np.cross(p2 - p1, p3 - p1) / np.linalg.norm(p2 - p1)) * 60)
            SightReduction.d_array.append(d)

            ax.set_title(f"{Sight.body_array[i]} || # {i + 1} || Scatter: %.2f' " % d, size=8, color='#f39c12')
            ax.text(time1.minute + .1, three, f'{Utilities.hmt_str(three)}', )
            ax.tick_params(axis='both', which='major', labelsize=6)

            d_dict[i] = d

        # Adjust subplot spacing based on the number of sights
        if Sight.num_of_sights % 2 == 0:
            plt.subplots_adjust(left=.062, bottom=.062, right=.97, top=.917, wspace=.2, hspace=.2)
        elif Sight.num_of_sights < 6:
            plt.subplots_adjust(left=.062, bottom=.062, right=.97, top=.917, wspace=.2, hspace=.2)
        else:
            plt.subplots_adjust(left=.057, bottom=.052, right=.979, top=.93, wspace=.248, hspace=.42)
            
       
        # Sorts d values closest to 0
        sorted_values = sorted(d_dict.values(), key=lambda x: abs(x))           
        sorted_dict = {}
        for i in sorted_values:
            for k in d_dict.keys():
                if d_dict[k] == i:
                    sorted_dict[k] = d_dict[k]
                    break
        pairs_recieved = []

        for i in sorted_dict.keys():
            pair = [Sight.body_array[i], i, Sight.sight_times[i]]
            pairs_recieved.append(pair)

        # just the body name
        unique_list = []
        unique_timechunks = []

        # traverse for all elements
        for x in Sight.body_array:
            # check if exists in unique_list or not
            if x not in unique_list:
                unique_list.append(x)

        # print list
        pairs_recieved.sort(key=lambda x: x[0])
        singlebodyelementarray = []
        if len(unique_list) == 1 and Sight.num_of_sights <= 3:
            self.top_unique = pairs_recieved

        elif len(unique_list) == 1 and Sight.num_of_sights > 3:
            try:
                for i in d_dict.keys():
                    singlebodyelement = (Sight.body_array[i], i, SightReduction.d_array[i], Sight.sight_times[i])
                    singlebodyelementarray.append(singlebodyelement)

                singlebody = Utilities.single_body_time_divide(singlebodyelementarray)

                self.top_unique = singlebody

            except:
                pass

        else:
            self.top_unique = []

            for x in pairs_recieved:
                if x[0] in unique_list:
                    self.top_unique.append(x)
                    top_unique_indexes.append(x[1])
                    unique_list.remove(x[0])

        top_unique_indexes.sort()

        return

    def calculate_lop_coordinates(self, dec, gha, ho, Bx_r, long):
        """Calculate latitude and longitude coordinates for a point on the LOP."""
        Lx_r = np.arcsin(np.sin(dec) * np.sin(ho) + np.cos(dec) * np.cos(ho) * np.cos(Bx_r))
        Lx_d = np.rad2deg(Lx_r)

        LHAx_r = np.arcsin((np.cos(ho) * np.sin(Bx_r)) / np.cos(Lx_r))
        LHAx_d = np.rad2deg(LHAx_r) % 360

        Longx_d = (LHAx_d + np.rad2deg(gha)) % 360
        Longx_d_2 = (np.rad2deg(gha) - LHAx_d)

        longitude_buffet = [360 - Longx_d, abs(Longx_d_2 + 180), (abs(Longx_d_2 + 180)) * -1, 
                            Longx_d * -1, Longx_d * -1, 180 - Longx_d_2, Longx_d_2]
        longitude_buffet = sorted(longitude_buffet)

        closest_long = min(longitude_buffet, key=lambda x: abs(x - long))

        return Lx_d, closest_long

    def bx_method(self):
        """Plots LOPs by computing pairs of x,y coordinates that lie on the LOP."""
        for i in range(Sight.num_of_sights):
            dec = Sight.dec_array_lop[i]
            gha = Sight.gha_array_lop[i]
            long = SightReduction.pos_array_lop_lon[0]
            lat = np.deg2rad(SightReduction.pos_array_lop_lat[0])
            lha = np.deg2rad(((np.rad2deg(gha) + long) % 360))
            hc_rad = np.arcsin((np.sin(dec) * np.sin(lat)) + (np.cos(dec) * np.cos(lat) * np.cos(lha)))

            z_rad = np.arccos((np.sin(lat) - np.sin(dec) * np.sin(hc_rad)) / (np.cos(dec) * np.cos(hc_rad)))
            z_rad = (360 - np.rad2deg(z_rad)) if np.rad2deg(lha) < 180 else np.rad2deg(z_rad)

            Bx_r_i = np.deg2rad(z_rad)

            latx_list = []
            longx_list = []
            ho = SightReduction.ho_array_rfix[i]

            # Calculate coordinates for both sides of Bx
            for Bx_r in [Bx_r_i + np.deg2rad(.75), Bx_r_i - np.deg2rad(.75)]:
                Lx_d, closest_long = self.calculate_lop_coordinates(dec, gha, ho, Bx_r, long)
                latx_list.append(Lx_d)
                longx_list.append(closest_long)

            SightReduction.latx_lists.append(latx_list)
            SightReduction.longx_lists.append(longx_list)

        return        
    
    def lop_plot(self):

        plt.style.use('dark_background')
        # plt.subplots(figsize=[6, 6])
        plt.figure(2)
        plt.clf()

        self.ax = plt.subplot(111)
        plt.subplots_adjust(left=.148, bottom=.121, right=.957, top=.929, wspace=.2, hspace=.2)

        self.ax.set_facecolor('#212946')

        # very light grey
        self.ax.grid(color='#2A3459')

        # latitude
        def y_fmt(x, y):
            """Uses Utilities.print_position to format matplotlib y-value ("dd°mm' N/S)
            Parameters
            ----------
            x : float
            matplotlib latitude value in dd.dddd
            """
            return Utilities.print_position(x, latitude=True)

        # longitude
        def x_fmt(y, x):
            """Uses Utilities.print_position to format matplotlib y-value ("ddd°mm' E/W) and constrains it to < 180 deg.
            Parameters
            ----------
            y : float
            matplotlib longitude value in ddd.dddd
            """
            if y > 180:
                y = y - 360
            elif y < -180:
                y = y + 360
            return Utilities.print_position(y, latitude=False)

        self.ax.yaxis.set_major_formatter(mticker.FuncFormatter(y_fmt))
        self.ax.xaxis.set_major_formatter(mticker.FuncFormatter(x_fmt))
        plt.xticks(rotation=45)

        for i in range(len(SightReduction.latx_lists)):
            y = SightReduction.latx_lists[i]
            x = SightReduction.longx_lists[i]

            plt.plot(SightReduction.longx_lists[i], SightReduction.latx_lists[i],
                     label=f'{Sight.body_array[i]} {Sight.sight_times[i]}')
            plt.legend(prop={'size': 7})
            plt.text(x[0] + .05, y[0] + .01, f'{Sight.body_array[i]}', size=9, color='#fff6')

        plt.scatter(SightReduction.pos_array_lop_lon[0], SightReduction.pos_array_lop_lat[0], marker='o', color='red')

        try:
            self.err_ellipse = Utilities.plot_cov_ellipse(self.res.hess_inv.todense(), (self.res.x[1], self.res.x[0]),
                                                        ax=self.ax, fc='none', edgecolor='#f39c12')

            self.ax.add_patch(self.err_ellipse)
        except:
            pass
 
        plt.scatter(self.dr_long, self.dr_lat, marker='+')
        plt.text(self.dr_long, self.dr_lat, f'{SightSession.dr_details[0][9].strftime("%H:%M")} UTC DR', size=9,
                 color='#00bc8c')

        plt.xlabel('Longitude', size=8, color='#fff6')
        plt.ylabel('Latitude', size=8, color='#fff6')

        plt.title(f'Computed Fix: {self.final_l_string} {self.final_lon_string}')

        final_position = [self.final_l_string, self.final_lon_string]
        SightReduction.final_position_array.append(final_position)

        # stats_header2 = ["N/S ERROR 68% PROB.", "E/W ERROR 68% PROB.", "N/S ERROR 95% PROB.", "E/W ERROR 95% PROB.",
        #                  "Sys. Err."]

        # stats_table_2 = [[f"(+/-) {np.round(((self.latitude_error / 2)), 2)}",
        #                   f" (+/-) {np.round(((self.longitude_error * np.cos(np.deg2rad(self.res.x[0])) / 2)), 2)}",
        #                   f"(+/-) {np.round(((self.latitude_error)), 2)}",
        #                   f" (+/-) {np.round(((self.longitude_error * np.cos(np.deg2rad(self.res.x[0])))), 2)}",
        #                   f'{np.round(np.mean(SightReduction.d_array), 2)}']]

        # SightReduction.stats_table_2.append(stats_table_2)

        # print(tabulate(stats_table_2, stats_header2, tablefmt='github'))
         
        anl_table = []
        anl_headers = ["BODY", "INDEX", "TIME"]
        for x in self.top_unique:
            string = [x[0], x[1],
                      Sight.sight_times[x[1]].strftime("%Y-%m-%d %H:%M:%S UTC")]
            anl_table.append(string)

        SightReduction.sight_anl_table.append(anl_table)
        sight_anl_tbl = tabulate(anl_table, anl_headers, tablefmt='github')
        # print(sight_anl_tbl)

        headers = ["INDEX", "BODY", "DR L", "DR λ", "TIME", 'GHA', 'DEC', 'AZ', 'Ho', 'Hc', 'Int.']

        self.bigdata = (tabulate(Sight.data_table, headers, tablefmt='rst'))
        gui_position_data = (
            SightSession.dr_details[0][9].strftime("%Y-%m-%d %H:%M:%S"), self.final_l_string, self.final_lon_string,
            Utilities.print_position(self.dr_lat, latitude=True), Utilities.print_position(self.dr_long, latitude=False))
        SightReduction.gui_position_table.append(gui_position_data)

        # print(self.bigdata)

        position_heads = ['Date', 'Computed Lat', 'Computed Long', 'DR Lat', 'DR Long']
        # print(tabulate([gui_position_data], position_heads, tablefmt='github'))
        ####################################################################################