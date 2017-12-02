import baseprocessor as bsp
import math
import geopy as gp
import numpy as np
import common
from geopy.distance import VincentyDistance



class AngleCalcBlock(bsp.FileProcessor):
    def __init__(self):
        self.children = []

    def process(self, inevents):
        #assert events data
        for event in inevents:
            if event.obs1_id:
                event.ob1_angle = self.calcangle(event.obs1)
            if event.obs2_id:
                event.ob2_angle = self.calcangle(event.obs2)
            if event.obs3_id:
                event.ob3_angle = self.calcangle(event.obs3)
        return inevents

    def calcangle(self, inputobs):
        #north is 0 degrees
        return math.pi/2 - math.atan(inputobs.sn_max_value/inputobs.ew_max_value)


class GreatCircleCalcBlock(bsp.FileProcessor):
    def __init__(self,vincentydist):
        self.children = []
        self.vincentydist = vincentydist

    def process(self, inevents):
        for event in inevents:
            # assert angle data
            dataarr = self.anglelocarr(event)
            for data in dataarr:
                obs = data['obs']
                angle = data['ang']
                data["pcircle"] = self.calccircle(angle,
                                                  obs.file.location.latitude,
                                                  obs.file.location.longitude)
                data["ncircle"] = self.calccircle(common.invertbearing(angle),
                                                  obs.file.location.latitude,
                                                  obs.file.location.longitude)
            if len(dataarr) == 2:
                event.pos_loc_lat, event.pos_loc_lon = self.resolveloc(dataarr[0], dataarr[1],
                                                                         circlestring="pcircle")
                event.neg_loc_lat, event.neg_loc_lon = self.resolveloc(dataarr[0], dataarr[1],
                                                                         circlestring="ncircle")

        return inevents


    def calccircle(self, ang, lat, lon):
        inip = gp.Point(lat, lon)
        target = VincentyDistance(kilometers=self.vincentydist).destination(inip, np.degrees(ang))
        return np.cross(common.tocartesianyxz(lon=inip.longitude, lat=inip.latitude),
                        common.tocartesianyxz(lon=target.longitude, lat=target.latitude))

    def intersec(self, first, second):
        line = np.cross(first, second);
        x1 = line / math.sqrt(np.power(line[0], 2) + np.power(line[1], 2) + np.power(line[2], 2))
        inter1 = gp.Point(latitude=np.degrees(np.arcsin(x1[2])),
                          longitude=np.degrees(np.arctan2(x1[1], x1[0])))
        inter2 = gp.Point(latitude=np.degrees(np.arcsin(-x1[2])),
                          longitude=np.degrees(np.arctan2(-x1[1], -x1[0])))
        return inter1, inter2

    def resolveloc(self, first, second, circlestring):
        pos1, pos2 = self.intersec(first[circlestring], second[circlestring])
        firstslarger = first['obs'].getpwr() > second['obs'].getpwr()
        p1 = first['obs'].file.location.getpoint()
        p2 = second['obs'].file.location.getpoint()
        firstcloser = VincentyDistance(p1, pos1).miles < VincentyDistance(p2, pos1).miles
        if (firstcloser and firstslarger) or (not firstcloser and not firstslarger):
            output = pos1
        else:
            output = pos2

        return output.latitude, output.longitude


    def anglelocarr(self,event):
        arr = []
        if event.ob1_angle:
            obs = event.obs1
            ang = event.ob1_angle
            arr.append({'obs': obs, 'ang': ang})
        if event.ob2_angle:
            obs = event.obs2
            ang = event.ob2_angle
            arr.append({'obs': obs, 'ang': ang})
        if event.ob3_angle:
            obs = event.obs3
            ang = event.ob3_angle
            arr.append({'obs': obs, 'ang': ang})
        return arr

    def writetoevent(self, event, pos1, pos2, neg1, neg2):
        event.pos_loc1_lat = pos1['lat']
        event.pos_loc1_lon = pos1['lon']
        event.pos_loc2_lat = pos2['lat']
        event.pos_loc2_lon = pos2['lon']
        event.neg_loc1_lat = neg1['lat']
        event.neg_loc1_lon = neg1['lon']
        event.neg_loc2_lat = neg2['lat']
        event.neg_loc2_lon = neg2['lon']







