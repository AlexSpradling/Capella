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

planets = load('de421.bsp')
ts = load.timescale()

class Utilities():

    def datetime(date, time):
        """ take user's date and time string values and concatenates into one datetime object.

        Parameters
        ----------
        date : str
            Always in UTC. 'yyyy-mm-dd'
        time : str
            Always in UTC. 'hh:mm:ss'

        """
        year, month, day = date.split('-')
        hour, minute, second = time.split(':')
        datetime = dt.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), tzinfo=utc)

        return datetime

    def hms(time):
        """ enter a number in hh.mmss format and, it will return a hh.hhhh value, mimics the hp-48gx sexagesimal
            math functions.

        Parameters
        ----------
        time : float
            Always in UTC. hh.mmss returned as hh.hhhh
        """
        time_hours, time_minutes = divmod(time, 1)
        time_minutes = time_minutes * 100
        time_minutes, time_seconds = divmod(time_minutes, 1)
        time_seconds = time_seconds * 100
        time = float(time_hours + (time_minutes / 60) + (time_seconds / 3600))

        return time

    def hmt_str(angle):
        """ enter a skyfield angle object value in degrees, returns a str value formatted "dd°mm'".

        Parameters
        ----------
        angle : float in degrees, hh.hhhh format
        """
        deg = int(angle)
        min = float(np.round(abs(angle) % 1 * 60, 1))
        if min < 10:
            min = str(min).zfill(4)

        return f"{deg}°{min}'"

    def hmt_str_2(angle):
        """ enter a skyfield angle object value in degrees, returns a str value formatted "dd-mm".

        Parameters
        ----------
        angle : skyfield Angle object in degrees
        """
        deg = int(angle)
        min = float(np.round(abs(angle) % 1 * 60, 1))
        if min < 10:
            min = str(min).zfill(4)

        return f"{deg}-{min}"

    def hmt_str_to_decimal_d(latstr, longstr):
        """ convert latitude and longitude string values into float values

        Parameters
        ----------
        latstr : str
            latitude str value formatted 'dd-mm.t-N/S'

        longstr : str
            longitude str value formatted 'ddd-mm.t-E/W'

        """
        deg, minutes, direction = latstr.split('-')
        latitude = (float(deg) + (float(minutes) / 60)) * (-1 if direction in 'S' else 1)
        deg, minutes, direction = longstr.split('-')
        longitude = (float(deg) + (float(minutes) / 60)) * (-1 if direction in 'W' else 1)

        return latitude, longitude

    def hh_mm_ss(time):
        """ enter a number in hh.mmss format and, it will split up hh, mm, ss as a tuple.

        Parameters
        ----------
        time : float
            Always in UTC. hh.mmss format.
        """

        time_hours, time_minutes = divmod(time, 1)

        time_minutes = float(time_minutes * 100)
        time_minutes, time_seconds = divmod(time_minutes, 1)
        time_seconds = float(time_seconds * 100)

        timehours = float(time_hours)
        timeminutes = round(float(time_minutes), 1)
        timeseconds = round(float(time_seconds), 1)

        return timehours, timeminutes, timeseconds

    def hms_out(time):
        """ enter a number in hh.hhhh format and, it will return a number in hh.mmss format.

        Parameters
        ----------
        time : float
            Always in UTC. hh.hhh format.
        """

        time_real = time
        time_hours, time_minutes = divmod(abs(time), 1)
        time_minutes = (time_minutes * 60)
        timeminutes = time_minutes / 100

        time_minutes, time_seconds = divmod(time_minutes, 1)
        time_seconds = time_seconds * 60
        timeseconds = (time_seconds) / 100

        minutesseconds = round((time_minutes + timeseconds) / 100, 4)
        if time_real < 0:
            time = round(((time_hours + minutesseconds) * -1), 4)
        else:
            time = round((time_hours + minutesseconds), 4)

        return time

    def print_position(position, latitude=True):
        """ receives a float value latitude or longitude, adds N, S, E, W suffix based on type and value and converts
        to str value using hmt_str function.

        Parameters
        ----------
        position : float
            latitude or longitude in hh.hhhh format

        latitude : bool
            whether or, not the position is a longitude, determines the N, S, E, W suffix to use.
        """
        if latitude == True:
            if position > 0:
                sign = 'N'
                print_latitude = position
            else:
                sign = 'S'
                print_latitude = position * -1

            final_string = (f'{Utilities.hmt_str(print_latitude)} {sign}')
        if latitude != True:
            if position > 0:
                sign = "E"
                print_longitude = position
            else:
                sign = "W"
                print_longitude = position * -1

            final_string = (f'{Utilities.hmt_str(print_longitude)} {sign}')

        return final_string

    def print_position2(position, latitude=True):
        """ receives a float value latitude or longitude, adds N, S, E, W suffix based on type and value and converts
        to str value using hmt_str_2 function.

        Parameters
        ----------
        position : float
        latitude or longitude in hh.hhhh format

        latitude : bool
        whether or, not the position is a longitude determines the N, S, E, W suffix to use.
        """
        if latitude == True:
            if position > 0:
                sign = 'N'
                print_latitude = position
            else:
                sign = 'S'
                print_latitude = position * -1

            final_string = (f'{Utilities.hmt_str_2(print_latitude)}-{sign}')
        else:
            if position > 0:
                sign = "E"
                print_longitude = position
            else:
                sign = "W"
                print_longitude = position * -1

            final_string = (f'{Utilities.hmt_str_2(print_longitude)}-{sign}')

        return final_string

    def single_body_time_divide(obj_array):
        """ receives an array of single body sight tuples and splits them into buckets based on a 900-second (15 min)
            interval, it will then return the sight-time with the lowest d-value from each bucket. For example,
            6 shots of the sun with a group of 3 at 1000, and 3 at or around LAN is 2 sessions. It will return
            2 buckets of 3 sun shots with the lowest d scatter value per bucket.

        Parameters
        ----------
        obj_array : list of tuples
        each tuple is : ('object', index, d-value, datetime)
        """
        split_points = []
        sorted(split_points)

        for i in range(len(obj_array)):
            try:
                delta = (dt.timedelta.total_seconds(obj_array[i + 1][3] - obj_array[i][3]))

                if abs(delta) > 900: split_point = i
                split_points.append(split_point)
            except:
                pass

        split_points = set(split_points)

        unique_list_splits = (list(split_points))

        bucket1 = []
        bucket2 = []
        bucket3 = []
        finalbucket = []

        if len(split_points) == 0:
            for i in obj_array:
                bucket1.append((i, 'Bucket1'))
                bucket1dvals = []
                for i in bucket1:
                    bucket1dvals.append(i[0][2])
                sorted_valuesb1 = sorted(bucket1dvals, key=lambda x: abs(x))
            for i in bucket1:

                if i[0][2] == sorted_valuesb1[0]:
                    match1 = (i[0][0], i[0][1])
                    return [match1]

        if len(unique_list_splits) == 1:
            for i in obj_array:
                if obj_array.index(i) <= unique_list_splits[0]:
                    bucket1.append((i, 'Bucket1'))
                    bucket1dvals = []
                    for i in bucket1:
                        bucket1dvals.append(i[0][2])
                    sorted_valuesb1 = sorted(bucket1dvals, key=lambda x: abs(x))
                else:
                    bucket2.append((i, 'Bucket2'))
                    bucket2dvals = []
                    for i in bucket2:
                        bucket2dvals.append(i[0][2])
                    sorted_valuesb2 = sorted(bucket2dvals, key=lambda x: abs(x))
            for i in bucket1:
                if i[0][2] == sorted_valuesb1[0]:
                    match1 = (i[0][0], i[0][1])
            for i in bucket2:
                if i[0][2] == sorted_valuesb2[0]:
                    match2 = (i[0][0], i[0][1])
                    return match1, match2

        if len(unique_list_splits) == 2:
            for i in obj_array:
                if obj_array.index(i) <= unique_list_splits[0]:
                    bucket1.append((i, 'Bucket1'))
                    bucket1dvals = []
                    for i in bucket1:
                        bucket1dvals.append(i[0][2])
                    sorted_valuesb1 = sorted(bucket1dvals, key=lambda x: abs(x))
                elif obj_array.index(i) <= unique_list_splits[1]:
                    bucket2.append((i, 'Bucket2'))
                    bucket2dvals = []
                    for i in bucket2:
                        bucket2dvals.append(i[0][2])
                    sorted_valuesb2 = sorted(bucket2dvals, key=lambda x: abs(x))
                else:
                    bucket3.append((i, 'Bucket3'))
                    bucket3dvals = []
                    for i in bucket3:
                        bucket3dvals.append(i[0][2])
                    sorted_valuesb3 = sorted(bucket3dvals, key=lambda x: abs(x))

            for i in bucket1:
                if i[0][2] == sorted_valuesb1[0]:
                    match1 = (i[0][0], i[0][1])
            for i in bucket2:
                if i[0][2] == sorted_valuesb2[0]:
                    match2 = (i[0][0], i[0][1])
            for i in bucket3:
                if i[0][2] == sorted_valuesb3[0]:
                    match3 = (i[0][0], i[0][1])
                    return match1, match2, match3

        return

    def time_of_phenomena(date, time, dr_lat, dr_long, course, speed):
        """ receives date, time and dr information, calculates the time of phenomena for am/pm civil/nautical
        twilights and then DR's to that time to obtain a second estimate time.

        Parameters
        ----------
        date : str
            'yyyy-mm-dd'
        time : str
            'hh:mm:ss'
        dr_lat : float
            dd.dddd format, S is -
        dr_long : float
            dd.dddd format , W is -
        course : float
            ddd format
        speed : float
            dd format
        """

        year, month, day = date.split('-')
        hour, minute, second = time.split(':')

        zd = round(dr_long / 15)

        tz = timezone(timedelta(hours=zd))
        gmt = timezone(timedelta(hours=0))

        datetime = dt.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), tzinfo=tz)

        # Figure out local midnight.

        midnight = datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        next_midnight = midnight + dt.timedelta(days=1)

        ts = load.timescale()
        t0 = ts.from_datetime(midnight)
        t1 = ts.from_datetime(next_midnight)
        eph = load('de421.bsp')
        position = wgs84.latlon(dr_lat, dr_long)
        f = almanac.dark_twilight_day(eph, position)
        f_1 = almanac.meridian_transits(eph, eph['Sun'], position)
        suntimes, sunevents = almanac.find_discrete(t0, t1, f_1)
        times, events = almanac.find_discrete(t0, t1, f)

        lan = suntimes[sunevents == 1]
        tsun = lan[0]
        sunstr = str(tsun.astimezone(tz))[:19]

        # second estimate for LAN

        sunstr = str(tsun.astimezone(tz))[:19]
        time_delta = dt.timedelta.total_seconds(tsun.astimezone(tz) - datetime)
        second_estimate_lat = DRCalc(dr_lat, dr_long, time_delta, course, speed).drlatfwds
        second_estimate_long = DRCalc(dr_lat, dr_long, time_delta, course, speed).drlongfwds
        position2 = wgs84.latlon(second_estimate_lat, second_estimate_long)
        f_1 = almanac.meridian_transits(eph, eph['Sun'], position2)
        suntimes, sunevents = almanac.find_discrete(t0, t1, f_1)
        lan = suntimes[sunevents == 1]
        tsun = lan[0]
        sunstr = str(tsun.astimezone(tz))[:19]
        sunstr2 = str(tsun.astimezone(gmt))[:19]

        # zd = round(second_estimate_long / 15)

        tz = timezone(timedelta(hours=zd))
        lanstr = (sunstr2, sunstr, 'L.A.N.')

        phenomenatimes = []

        previous_e = f(t0).item()
        for t, e in zip(times, events):
            tstr = str(t.astimezone(tz))[:16]
            tstr2 = str(t.astimezone(gmt))[:16]

            if previous_e < e:
                string = (tstr2, tstr, f'{almanac.TWILIGHTS[e]} starts [{zd}]')
                phenomenatimes.append(string)
                if len(phenomenatimes) == 4:
                    phenomenatimes.append(lanstr)

            else:
                string = (tstr2, tstr, f'{almanac.TWILIGHTS[previous_e]} ends [{zd}]')
                phenomenatimes.append(string)
                if len(phenomenatimes) == 4:
                    phenomenatimes.append(lanstr)

            previous_e = e

        return phenomenatimes

    def get_gha_dec(body, datetime, latitude, longitude):
        """ receives celestial object, date and position and returns gha, dec, ghaa, alt, az and magnitude using
        the Skyfield library, hipparcos catalog and DE421 database.

        Parameters
        ----------
        body : str
            Celestial object in question, upper limb and lower limb are UL or LL respectively.
        datetime: dt object

        latitude: float
            dd.dddd format, S is -

        longitude: float
            ddd.dddd format, W is -
        """

        planets = load('de421.bsp')
        ts = load.timescale()
        t = ts.utc(datetime)

        if body == 'SunLL' or body == 'SunUL':
            celestial_body = planets['Sun']
            mag = -26.74
        elif body == 'MoonLL' or body == 'MoonUL':
            celestial_body = planets['Moon']
            mag = - 12.6
        elif body == 'Mars':
            celestial_body = planets['Mars']
            mag = 1.4
        elif body == 'Venus':
            celestial_body = planets['Venus']
            mag = -4.9
        elif body == 'Jupiter':
            celestial_body = planets['Jupiter Barycenter']
            mag = -2.9
        elif body == 'Saturn':
            celestial_body = planets['Saturn Barycenter']
            mag = .75
        elif body == 'Uranus':
            celestial_body = planets['Uranus Barycenter']
            mag = 5.38
        elif body == 'Mercury':
            celestial_body = planets['Mercury']
            mag = .28
        else:
            which_star = body
            hid = Sight.named_star_dict.get(which_star)
            celestial_body = Star.from_dataframe(df.loc[hid])
            mag = df['magnitude'][hid]

        obs = planets['Earth']
        position = obs + Topos(latitude_degrees=(latitude), longitude_degrees=(longitude))
        astro = position.at(t).observe(celestial_body)
        app = astro.apparent()
        astrometric = obs.at(t).observe(celestial_body)
        apparent = obs.at(t).observe(celestial_body).apparent()
        alt, az, distance = app.altaz()
        ra, dec, distance, = apparent.radec(epoch='date')
        ghaa = Angle(degrees=(t.gast) * 15)
        gha = Angle(degrees=((t.gast - ra.hours) * 15 % 360 - 0))

        return gha, dec, ghaa, alt, az, mag

    def plot_cov_ellipse(cov, pos, nstd=2, ax=None, **kwargs):
        """ Generates confidence ellipse in matplot lib.

        Parameters
        ----------
        cov : np.array
            Covariance matrix from L-BFGS-B function
        pos : tuple
            x, y position for center of ellipse
        nstd : int
            number of standard deviations.
        """
        def eigsorted(cov):
            vals, vecs = np.linalg.eigh(cov)
            order = vals.argsort()[::-1]
            return vals[order], vecs[:, order]

        if ax is None:
            ax = plt.gca()

        vals, vecs = eigsorted(cov)

        theta = np.degrees(np.arctan2(*vecs[:, 0][::-1])) * -1

        # Width and height are "full" widths, not radius
        width, height = 2 * nstd * np.sqrt(vals)

        ellip = Ellipse(xy=pos, width=height / 100, height=width / 100, angle=theta, **kwargs)

        ax.add_artist(ellip)
        return ellip

class DRCalc():
    """
    dr_calc() : will calculate a mercator sailing based on a position,
    C/S and a dt.dimedelta object. It can DR from a position either forwards or backwards
    using the recriprocal of the DR course. This is useful for the sight analysis functions,
    since the function starts from the Least Squares fix and then DR's backwards to the time of each sight,
    this is allows the initial DR position to be extremely inaccurate, yet
    still provide an effective fit-slope analysis.
    """

    def __init__(self, init_lat, init_long, timedelta, course, speed):
        self.init_lat = float(init_lat)
        self.init_long = float(init_long)
        self.timedelta = float(timedelta) / 3600
        self.course = float(course)
        self.speed = float(speed)
        self.dr_coord_calc_fwd()
        self.dr_coord_calc_bwd()

        return

    def dr_coord_calc_fwd(self):
        self.distance = self.timedelta * self.speed
        if self.course == 90:
            self.lat2 = self.init_lat
            self.dlo = (self.distance / np.cos(np.deg2rad(self.init_lat))) / 60
        elif self.course == 270:
            self.lat2 = self.init_lat
            self.dlo = -1 * (self.distance / np.cos(np.deg2rad(self.init_lat))) / 60
        else:
            if 0 < self.course < 90:
                self.courseangle = self.course
            elif 90 < self.course < 180:
                self.courseangle = 180 - self.course
            elif 180 < self.course < 270:
                self.courseangle = self.course + 180
            else:
                self.courseangle = 360 - self.course
            self.lat2 = (self.distance * np.cos(np.deg2rad(self.course))) / 60 + self.init_lat
            mpartsinitial = 7915.7045 * np.log10(
                np.tan(np.pi / 4 + (np.deg2rad(self.init_lat) / 2))) - 23.2689 * np.sin(
                np.deg2rad(self.init_lat))
            mpartssecond = 7915.7045 * np.log10(np.tan(np.pi / 4 + (np.deg2rad(self.lat2) / 2))) - 23.2689 * np.sin(
                np.deg2rad(self.lat2))
            littlel = mpartssecond - mpartsinitial
            self.dlo = (littlel * np.tan(np.deg2rad(self.course))) / 60
        self.drlatfwds = self.lat2
        self.drlongfwds = self.init_long + self.dlo
        if self.drlongfwds >= 180:
            self.drlongfwds = self.drlongfwds - 360

        return

    def dr_coord_calc_bwd(self):

        self.course = (self.course - 180) % 360
        self.distance = self.timedelta * self.speed
        if self.course == 90:
            self.lat2 = self.init_lat
            self.dlo = (self.distance / np.cos(np.deg2rad(self.init_lat))) / 60
        elif self.course == 270:
            self.lat2 = self.init_lat
            self.dlo = -1 * (self.distance / np.cos(np.deg2rad(self.init_lat))) / 60
        else:
            if 0 < self.course < 90:
                self.courseangle = self.course
            elif 90 < self.course < 180:
                self.courseangle = 180 - self.course
            elif 180 < self.course < 270:
                self.courseangle = self.course + 180
            else:
                self.courseangle = 360 - self.course

            self.lat2 = (self.distance * np.cos(np.deg2rad(self.course))) / 60 + self.init_lat
            mpartsinitial = 7915.7045 * np.log10(
                np.tan(np.pi / 4 + (np.deg2rad(self.init_lat) / 2))) - 23.2689 * np.sin(
                np.deg2rad(self.init_lat))
            mpartssecond = 7915.7045 * np.log10(np.tan(np.pi / 4 + (np.deg2rad(self.lat2) / 2))) - 23.2689 * np.sin(
                np.deg2rad(self.lat2))
            littlel = mpartssecond - mpartsinitial
            self.dlo = (littlel * np.tan(np.deg2rad(self.course))) / 60

        self.drlatbackwards = self.lat2
        self.drlongbackwards = self.init_long + self.dlo
        if self.drlongbackwards >= 180:
            self.drlongbackwards = self.drlongbackwards - 360
        return

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

    def vector_reduction(self):
        """computes fix using L-BFGS-B minimization, given the Sight and Sight_session information provided. The
        objective function minimizes the square root of the sum of the intercepts divided by the number of sights.
        """

        def obj_function(params):
            """ Objective Function to be minimized
            params
            ------
            int_sum : list
                sum of intercept values
            gha : float
                dd.dddd format, in radians
            dec : float
                dd.dddd format, in radians
            lha : float
                dd.dddd format, in radians, mod 360
            hc : Angle
                dd.dddd format, computed in radians
            ho : float
                Sight_Reduction.ho_array_rfix value in radians
            int : float
                (hc-ho) in radians, value is squared and then appended to int_sum array
            val : int
                number of Sight objects initialized
            """
            int_sum = []
            lat, long = params
            for i in range(len(Sight.body_array)):
                gha = Sight.gha_array_lop[i]
                dec = Sight.dec_array_lop[i]
                lha = long + np.rad2deg(gha) % 360
                hc = Angle(radians=(np.arcsin(
                    np.sin(np.deg2rad(lat)) * np.sin(dec) + np.cos(np.deg2rad(lat)) * np.cos(dec) * np.cos(
                        np.deg2rad(lha)))))
                ho = SightReduction.ho_array_rfix[i]
                int = ho - hc.radians
                int_sum.append(int ** 2)
                val = Sight.num_of_sights
            # Square root of the sum of the intercepts/num of sights
            return np.sqrt(np.sum(int_sum) / val)

        self.dr_lat = DRCalc(SightSession.dr_details[0][1], SightSession.dr_details[0][2],
                             dt.timedelta.total_seconds(
                                 SightSession.dr_details[0][9] - SightSession.dr_details[0][0]),
                             SightSession.dr_details[0][3].degrees, SightSession.dr_details[0][4]).drlatfwds
        self.dr_long = DRCalc(SightSession.dr_details[0][1], SightSession.dr_details[0][2],
                              dt.timedelta.total_seconds(
                                  SightSession.dr_details[0][9] - SightSession.dr_details[0][0]),
                              SightSession.dr_details[0][3].degrees, SightSession.dr_details[0][4]).drlongfwds

        # initial_guess is a DR position computed using the dr_calc class from the Sight_session DR position
        # to the fix_time specified using the course and speed information provided in Sight_session.dr_details
        initial_guess = np.array([self.dr_lat, self.dr_long])

        # L-BFGS-B REDUCTION
        self.res = optimize.minimize(obj_function, initial_guess, method='L-BFGS-B')

        # Create table for scipy optimization results
        headers = ["Success", "Iterations", "Func. Value"]
        res_info = [[self.res.success, self.res.nit, self.res.fun]]
        self.res_info_str = tabulate(res_info, headers=headers)

        print('L-BFGS-B Reduction')
        print(self.res_info_str)
        tmp_i = np.zeros(len(self.res.x))

        # ERRORS FROM INV. HESSIAN
        for i in range(len(self.res.x)):
            tmp_i[i] = 1.0
            hess_inv_i = self.res.hess_inv(tmp_i)[i]
            uncertainty_i = np.sqrt(max(1, abs(self.res.fun)) * hess_inv_i)
            tmp_i[i] = 0.0
            if i == 0:
                self.latitude_error = uncertainty_i
            else:
                self.longitude_error = uncertainty_i

        # 95% error
        huh = np.sqrt(np.diag(self.res.hess_inv.todense()))

        # print(self.res)

        # COMPUTED VALUES FOR LATITUDE AND LONGITUDE
        self.fit_latitude = Angle(degrees=(self.res.x[0]))
        if self.res.x[1] > 180:
            self.res.x[1] = self.res.x[1]- 360
        elif self.res.x[1] < -180:
            self.res.x[1] = self.res.x[1] + 360
        self.fit_longitude = Angle(degrees=(self.res.x[1]))


        ########################################################################################################################

        ########################################################################################################################
        self.fixtime = SightSession.dr_details[0][9]
        if self.fit_latitude.degrees > 0:
            lat_sign = 'N'
            self.print_latitude = self.fit_latitude
        else:
            lat_sign = 'S'
            self.print_latitude = Angle(degrees=(self.fit_latitude.degrees * -1))
        if self.fit_longitude.degrees > 0:
            long_sign = "E"
            self.print_longitude = self.fit_longitude
        else:
            long_sign = "W"
            self.print_longitude = Angle(degrees=(self.fit_longitude.degrees * -1))

        self.final_l_string = f'L {Utilities.hmt_str(self.print_latitude.degrees)} {lat_sign}'
        self.final_lon_string = f'λ {Utilities.hmt_str(self.print_longitude.degrees)} {long_sign}'

        SightReduction.position_array_l.append(self.final_l_string)
        SightReduction.position_array_lon.append(self.final_lon_string)
        SightReduction.pos_array_lop_lat.append(self.fit_latitude.degrees)
        SightReduction.pos_array_lop_lon.append(self.fit_longitude.degrees)

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

    def sight_analysis(self):
        """the goal of the sight analyzer is to work backwards from the final computed position, DR to each time and
        compute an HS value for a time 1-minute on either side of the actual sight time, this creates a computed
        slope that the sight can be compared against. """

        lat = float(self.fit_latitude.degrees)
        long = float(self.fit_longitude.degrees)
        course = SightSession.dr_details[0][3].degrees
        speed = SightSession.dr_details[0][4]

        for i in range(Sight.num_of_sights):
            """calculates lat and long dr positions for the EXACT time of each sight, working backwards from the 
            final fix """

            previous_lat = DRCalc(lat, long, SightReduction.time_delta_array[i], course, speed).drlatbackwards
            previous_long = DRCalc(lat, long, SightReduction.time_delta_array[i], course, speed).drlongbackwards

            SightReduction.sight_analysis_lat_time_of_sight.append(previous_lat)
            SightReduction.sight_analysis_long_time_of_sight.append(previous_long)
            self.datetime = Sight.sight_times[i]

            body = Sight.body_array[i]
            ephem = Utilities.get_gha_dec(body, self.datetime, SightReduction.sight_analysis_lat_time_of_sight[i],
                                          SightReduction.sight_analysis_long_time_of_sight[i])

            gha = ephem[0]
            dec = ephem[1]
            lat_hc = Angle(degrees=(SightReduction.sight_analysis_lat_time_of_sight[i]))
            long_hc = Angle(degrees=(SightReduction.sight_analysis_long_time_of_sight[i]))
            lha = Angle(degrees=(gha.degrees + long_hc.degrees))
            hc = np.arcsin((np.sin(lat_hc.radians) * np.sin(dec.radians)) + (
                    np.cos(lat_hc.radians) * np.cos(dec.radians) * np.cos(lha.radians)))

            SightReduction.hc_timeofsight.append(np.rad2deg(hc))

        for i in range(Sight.num_of_sights):
            """computes the DR position 1 minute AHEAD of the time of the sight using the set course/speed
            information """
            previous_lat = DRCalc(lat, long, (SightReduction.time_delta_array[i]) + 60, course, speed).drlatbackwards
            previous_long = DRCalc(lat, long, (SightReduction.time_delta_array[i]) + 60, course,
                                   speed).drlongbackwards

            SightReduction.sight_analysis_lat_plus_one.append(previous_lat)
            SightReduction.sight_analysis_long_plus_one.append(previous_long)
            self.datetime = Sight.sight_times[i] + dt.timedelta(seconds=60)

            body = Sight.body_array[i]
            ephem = Utilities.get_gha_dec(body, self.datetime, SightReduction.sight_analysis_lat_plus_one[i],
                                          SightReduction.sight_analysis_long_plus_one[i])

            gha = ephem[0]
            dec = ephem[1]

            lat_hc = Angle(degrees=(SightReduction.sight_analysis_lat_time_of_sight[i]))
            long_hc = Angle(degrees=(SightReduction.sight_analysis_long_time_of_sight[i]))
            lha = Angle(degrees=(gha.degrees + long_hc.degrees))
            hc = np.arcsin((np.sin(lat_hc.radians) * np.sin(dec.radians)) + (
                    np.cos(lat_hc.radians) * np.cos(dec.radians) * np.cos(lha.radians)))

            SightReduction.hc_plusone.append(np.rad2deg(hc))

        for i in range(Sight.num_of_sights):
            """computes DR lat and long one minute BEHIND the time of the sight using course/speed information"""

            previous_lat = DRCalc(lat, long, SightReduction.time_delta_array[i] - 60, course, speed).drlatbackwards
            previous_long = DRCalc(lat, long, SightReduction.time_delta_array[i] - 60, course,
                                   speed).drlongbackwards

            SightReduction.sight_analysis_lat_minus_one.append(previous_lat)
            SightReduction.sight_analysis_long_minus_one.append(previous_long)
            self.datetime = Sight.sight_times[i] - dt.timedelta(seconds=60)

            body = Sight.body_array[i]
            ephem = Utilities.get_gha_dec(body, self.datetime, SightReduction.sight_analysis_lat_minus_one[i],
                                          SightReduction.sight_analysis_long_minus_one[i])

            gha = ephem[0]
            dec = ephem[1]

            lat_hc = Angle(degrees=(SightReduction.sight_analysis_lat_time_of_sight[i]))
            long_hc = Angle(degrees=(SightReduction.sight_analysis_long_time_of_sight[i]))
            lha = Angle(degrees=(gha.degrees + long_hc.degrees))
            hc = np.arcsin((np.sin(lat_hc.radians) * np.sin(dec.radians)) + (
                    np.cos(lat_hc.radians) * np.cos(dec.radians) * np.cos(lha.radians)))

            SightReduction.hc_minusone.append(np.rad2deg(hc))

    d_array = []

    def scatter_plot_analyzer(self):
        """Matplotlib plotting function for sight_analysis function."""
        d_dict = {}
        top_unique_indexes = []
        plt.subplots(figsize=[7, 7])
        plt.figure(1)
        plt.clf()

        def y_fmt(y, x):
            """Uses Utilities.hmt_str to format matplotlib y-value ("dd°mm')
            Parameters
            ----------
            y : float
            matplotlib longitude value in ddd.dddd
            """
            return Utilities.hmt_str(y)

        def datetime_to_float(d):
            """Converts dt.datetime value to timestamp() value
            Parameters
            ----------
            d : dt.datetime
            datetime object that is converted to dt.timestamp()
            """
            return d.timestamp()

        for i in range(Sight.num_of_sights):

            plt.style.use('dark_background')

            one = SightReduction.hc_plusone[i]
            two = SightReduction.hc_minusone[i]
            three = Sight.ho_array[i]
            four = SightReduction.hc_timeofsight[i]

            time1 = Sight.sight_times[i]
            time_before = Sight.sight_times[i] + dt.timedelta(seconds=60)
            time_after = Sight.sight_times[i] - dt.timedelta(seconds=60)

            x = np.array([time_before, time1, time_after])

            y = np.array([two, four, one])

            # add linear regression line to scatterplot

            if Sight.num_of_sights % 2 == 0:
                gs = gridspec.GridSpec(2, int(Sight.num_of_sights / 2))
                self.ax11 = plt.subplot(gs[i])
                self.ax11.yaxis.set_major_formatter(mticker.FuncFormatter(y_fmt))
                self.ax11.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))
                self.ax11.set_facecolor('#212946')
                self.ax11.grid(color='#2A3459')
                plt.subplots_adjust(left=.062, bottom=.062, right=.97, top=.917, wspace=.2, hspace=.2)

            else:

                if Sight.num_of_sights < 6:
                    gs = gridspec.GridSpec(nrows=2, ncols=3)
                    self.ax11 = plt.subplot(gs[i])
                    self.ax11.yaxis.set_major_formatter(mticker.FuncFormatter(y_fmt))
                    self.ax11.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))
                    self.ax11.set_facecolor('#212946')
                    self.ax11.grid(color='#2A3459')
                    plt.subplots_adjust(left=.062, bottom=.062, right=.97, top=.917, wspace=.2, hspace=.2)

                elif 6 < Sight.num_of_sights < 9:
                    gs = gridspec.GridSpec(nrows=2, ncols=4)
                    self.ax11 = plt.subplot(gs[i])
                    self.ax11.yaxis.set_major_formatter(mticker.FuncFormatter(y_fmt))
                    self.ax11.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))
                    self.ax11.set_facecolor('#212946')
                    self.ax11.grid(color='#2A3459')

                else:
                    gs = gridspec.GridSpec(nrows=4, ncols=4)
                    self.ax11 = plt.subplot(gs[i])
                    self.ax11.yaxis.set_major_formatter(mticker.FuncFormatter(y_fmt))
                    self.ax11.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))
                    self.ax11.set_facecolor('#212946')
                    self.ax11.grid(color='#2A3459')
                    plt.subplots_adjust(left=.057, bottom=.052, right=.979, top=.93, wspace=.248, hspace=.42)

            plt.plot(x, y)


            plt.scatter(time1, three, color='red')


            p1 = np.array([datetime_to_float(time_after), one], dtype=object)
            p2 = np.array([datetime_to_float(time_before), two], dtype=object)
            p3 = np.array([datetime_to_float(time1), three], dtype=object)
            p4 = np.array([datetime_to_float(time1), four], dtype=object)

            d = float((np.cross(p2 - p1, p3 - p1) / np.linalg.norm(p2 - p1)) * 60)

            SightReduction.d_array.append(d)

            plt.title(f"{Sight.body_array[i]} || # {i + 1} || Scatter: %.2f' " % d, size=8, color='#f39c12')

            # plt.text(time1.minute, four, f'{Utilities.hmt_str(four)}', size=8)
            plt.text(time1.minute + .1, three, f'{Utilities.hmt_str(three)}', )
            plt.yticks(rotation=45, size=6)
            plt.xticks(rotation=-45, size=6)

            # scatter values
            d_dict[i] = SightReduction.d_array[i]

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

    """
    def error_trapping(self):
        print(f'L-BFGS Function Value: {self.res.fun *100}')
        if (self.res.fun*100) >.1:
            print('FIX QUALITY IS LOW - note suspected errors listed below, computed fix and plotted fix are unreliable.')
            print('')
            #check for time input errors
            for i in Sight.sight_times:
                time_delta = dt.timedelta.total_seconds(plot.session.fixtime - i)
                if abs(time_delta) >= 3600:
                    type_of_error = 'Time Entry Error'
                    error_sight = Sight.body_array[Sight.sight_times.index(i)]
                    break
                else:
                    type_of_error = 'Unknown Body Error'
                    unknownbodypossibilities = []
                    for b in Sight.intercept_array:
                        if abs(b * 60) > 100:
                            error_sight = Sight.body_array[Sight.intercept_array.index(b)]


                            obs = planets['Earth']
                            position = obs + Topos(latitude_degrees=(Sight.computedlat[Sight.intercept_array.index(b)]),
                                                   longitude_degrees=(Sight.computedlong[Sight.intercept_array.index(b)]))

                            self.datetime = Sight.sight_times[Sight.intercept_array.index(b)]
                            self.t = ts.utc(self.datetime)


                            for i in Sight.named_star_dict:
                                hid = Sight.named_star_dict.get(i)
                                celestial_body = Star.from_dataframe(df.loc[hid])
                                astro = position.at(self.t).observe(celestial_body)
                                app = astro.apparent()
                                astrometric = obs.at(self.t).observe(celestial_body)
                                apparent = obs.at(self.t).observe(celestial_body).apparent()
                                alt, az, distance = app.altaz()
                                ra, dec, distance, = apparent.radec(epoch='date')


                                for x in Sight.ho_array:
                                    intercept = abs(x-alt.degrees)
                                    if alt.degrees > 0 and intercept < .5 and i not in Sight.body_array:
                                        candidate = [Sight.sight_times[Sight.intercept_array.index(b)],str(i),alt,
                                                     round(float(x-alt.degrees)*60,2),np.round(az.degrees,1)]
                                        unknownbodypossibilities.append(candidate)

            unknownbodypossibilities.sort(key=lambda y: y[3],reverse=True)
            print(f"ERROR TRAPPING: {type_of_error}")
            print("")
            print(f'ERRONEOUS SIGHT ENTRY ERROR LIKELY, SUSPECTED SIGHT:')
            print(f'{error_sight}')
            print('')
            if type_of_error == 'Unknown Body Error':
                print('You likely observed:')
                headers = ['Time','BODY', 'Alt', 'INTERCEPT', 'AZIMUTH']

                print(tabulate(unknownbodypossibilities,headers))

        return
    """

    def bx_method(self):
        """Plots LOP's in matplotlib by computing pairs of x,y coordinates that lie on the LOP, the pairs are then
        connected to form the line. B_x is the bearing from the sun to a point on the LOP. By incrementing B_x by +/-
        .75 degrees of arc, points along the LOP are generated and the LOP is traced out. """

        for i in range(Sight.num_of_sights):
            """iterate through sights, use index to extract relevant info from other arrays"""
            self.dec = Sight.dec_array_lop[i]
            self.gha = Sight.gha_array_lop[i]
            self.long = SightReduction.pos_array_lop_lon[0]
            self.lat = np.deg2rad(SightReduction.pos_array_lop_lat[0])
            self.lha = np.deg2rad(((np.rad2deg(self.gha) + self.long) % 360))
            self.hc_rad = np.arcsin((np.sin(self.dec) * np.sin(self.lat)) + (
                    np.cos(self.dec) * np.cos(self.lat) * np.cos(self.lha)))

            self.z_rad = np.arccos(
                (np.sin(self.lat) - np.sin(self.dec) * np.sin(self.hc_rad)) / (np.cos(self.dec) * np.cos(self.hc_rad)))

            if np.rad2deg(self.lha) < 180:
                self.z_rad = (360 - np.rad2deg(self.z_rad))
            else:
                self.z_rad = np.rad2deg(self.z_rad)

            self.Bx_r_i = np.deg2rad(self.z_rad)

            latx_list = []
            longx_list = []
            ho = SightReduction.ho_array_rfix[i]
            Bx_r = self.Bx_r_i
            Bx_r_ = self.Bx_r_i

            # One iteration works, figure out how to do more without overlapping
            for b in range(1):
                """add .75 arc degrees to BX_r"""
                # Bearing from sun to point on LOP, increased by .75 degrees
                Bx_r = Bx_r + np.deg2rad(.75)
                # Calculate latitude of point x on LOP. sin L_x = sin d * sin Ho + cos d * cos Ho * cos B_x
                Lx_r = np.arcsin(np.sin(self.dec) * np.sin(ho) + np.cos(self.dec) * np.cos(ho) * np.cos(Bx_r))
                Lx_d = np.rad2deg(Lx_r)
                # append Latitude value in degrees to latx_list
                latx_list.append(Lx_d)
                # Calculate LHA of point x on LOP. sin LHA_x = cos Ho * sin B_x / cos L_x
                LHAx_r = np.arcsin((np.cos(ho) * np.sin(Bx_r)) / np.cos(Lx_r))
                LHAx_d = np.rad2deg(LHAx_r) % 360

                # finding the Longitude of point x on LOP from LHA - not as straightforward as it would seem!
                Longx_d = (LHAx_d + np.rad2deg(self.gha)) % 360
                Longx_d_2 = (np.rad2deg(self.gha) - LHAx_d)
                one = 360 - Longx_d
                two = abs(Longx_d_2 + 180)
                three = two * -1
                four = Longx_d * -1
                five = three * -1
                six = 180 - Longx_d_2
                seven = Longx_d_2
                longitude_buffet = sorted([one, two, three, four, five, six, seven])
                # find closest long from longitude_buffet
                closest_long = longitude_buffet[
                    min(range(len(longitude_buffet)), key=lambda i: abs(longitude_buffet[i] - self.long))]
                # list of Longitudes that exists on LOP, selected from the longitude_buffet
                longx_list.append(closest_long)

                ###################################
                """Same process as above but reversed for other side of B_x"""
                # Bearing from sun to point on LOP, decreased by .75 degrees
                Bx_r_ = Bx_r_ - np.deg2rad(.75)
                # Calculate latitude of point x on LOP. sin L_x = sin d * sin Ho + cos d * cos Ho * cos B_x
                Lx_r = np.arcsin(np.sin(self.dec) * np.sin(ho) + np.cos(self.dec) * np.cos(
                    ho) * np.cos(Bx_r_))
                Lx_d = np.rad2deg(Lx_r)
                # append Latitude value in degrees to latx_list
                latx_list.append(Lx_d)
                # Calculate LHA of point x on LOP. sin LHA_x = cos Ho * sin B_x / cos L_x
                LHAx_r = np.arcsin((np.cos(ho) * np.sin(Bx_r_)) / np.cos(Lx_r))
                LHAx_d = np.rad2deg(LHAx_r) % 360

                # finding the Longitude of point x on LOP from LHA - not as straightforward as it would seem!
                Longx_d = (LHAx_d + np.rad2deg(self.gha)) % 360
                Longx_d_2 = (np.rad2deg(self.gha) - LHAx_d)
                one = 360 - Longx_d
                two = abs(Longx_d_2 + 180)
                three = two * -1
                four = Longx_d * -1
                five = three * -1
                six = 180 - Longx_d_2
                seven = Longx_d_2
                longitude_buffet = sorted([one, two, three, four, five, six, seven])
                # find closest long from longitude_buffet
                closest_long = longitude_buffet[
                    min(range(len(longitude_buffet)), key=lambda i: abs(longitude_buffet[i] - self.long))]
                # list of Longitudes that exists on LOP, selected from the longitude_buffet
                longx_list.append(closest_long)

            SightReduction.latx_lists.append(latx_list)
            SightReduction.longx_lists.append(longx_list)

        return

    def lop_plot(self):
        """Matplotlib plotting function. Only fires once all, of the required information is loaded into the arrays."""

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

        self.err_ellipse = Utilities.plot_cov_ellipse(self.res.hess_inv.todense(), (self.res.x[1], self.res.x[0]),
                                                      ax=self.ax, fc='none', edgecolor='#f39c12')

        self.ax.add_patch(self.err_ellipse)

        plt.scatter(self.dr_long, self.dr_lat, marker='+')
        plt.text(self.dr_long, self.dr_lat, f'{SightSession.dr_details[0][9].strftime("%H:%M")} UTC DR', size=9,
                 color='#00bc8c')

        plt.xlabel('Longitude', size=8, color='#fff6')
        plt.ylabel('Latitude', size=8, color='#fff6')

        plt.title(f'Computed Fix: {self.final_l_string} {self.final_lon_string}')

        final_position = [self.final_l_string, self.final_lon_string]
        SightReduction.final_position_array.append(final_position)

        stats_header2 = ["N/S ERROR 68% PROB.", "E/W ERROR 68% PROB.", "N/S ERROR 95% PROB.", "E/W ERROR 95% PROB.",
                         "Sys. Err."]

        stats_table_2 = [[f"(+/-) {np.round(((self.latitude_error / 2)), 2)}",
                          f" (+/-) {np.round(((self.longitude_error * np.cos(np.deg2rad(self.res.x[0])) / 2)), 2)}",
                          f"(+/-) {np.round(((self.latitude_error)), 2)}",
                          f" (+/-) {np.round(((self.longitude_error * np.cos(np.deg2rad(self.res.x[0])))), 2)}",
                          f'{np.round(np.mean(SightReduction.d_array), 2)}']]

        SightReduction.stats_table_2.append(stats_table_2)

        print(tabulate(stats_table_2, stats_header2))
        anl_table = []
        anl_headers = ["BODY", "INDEX", "TIME"]
        for x in self.top_unique:
            string = [x[0], x[1],
                      Sight.sight_times[x[1]].strftime("%Y-%m-%d %H:%M:%S UTC")]
            anl_table.append(string)

        SightReduction.sight_anl_table.append(anl_table)
        sight_anl_tbl = tabulate(anl_table, anl_headers, tablefmt='rst')
        print(sight_anl_tbl)

        headers = ["INDEX", "BODY", "DR L", "DR λ", "TIME", 'GHA', 'DEC', 'AZ', 'Ho', 'Hc', 'Int.']

        self.bigdata = (tabulate(Sight.data_table, headers, tablefmt='rst'))
        gui_position_data = (
            SightSession.dr_details[0][9].strftime("%Y-%m-%d %H:%M:%S UTC"), self.final_l_string, self.final_lon_string,
            Utilities.print_position(self.dr_lat, latitude=True), Utilities.print_position(self.dr_long, latitude=False))
        SightReduction.gui_position_table.append(gui_position_data)

        # print(self.bigdata)

        position_heads = ['Date', 'Computed Lat', 'Computed Long', 'DR Lat', 'DR Long']
        # print(tabulate([gui_position_data], position_heads, tablefmt='rst'))
        ####################################################################################