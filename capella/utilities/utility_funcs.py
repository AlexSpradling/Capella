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

from capella.utilities.dead_reckoning import DRCalc



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

         # Dictionary for named stars and their hipparcos id
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
            hid = named_star_dict.get(which_star)
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

