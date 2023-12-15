import numpy as np


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

