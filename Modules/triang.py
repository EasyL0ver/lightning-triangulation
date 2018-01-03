import linelement as bsp
import math
import geopy as gp
import numpy as np
import common
from geopy.distance import VincentyDistance


class AngleCalcBlock(bsp.BaseProcessor):
    def calcangles(self, inevents):
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
        #rad = math.pi/2 - math.atan(inputobs.sn_max_value/inputobs.ew_max_value)
        rad = math.pi / 2 - math.atan(inputobs.ew_max_value / inputobs.sn_max_value)
        #rad = math.pi/2 - math.atan2(inputobs.sn_max_value, inputobs.ew_max_value)
        return rad
        #return math.atan(inputobs.sn_max_value / inputobs.ew_max_value)

    def children(self):
        return self._children

    def prcmodes(self):
        return self._prcmodes

    def __init__(self):
        self._children = []
        self._prcmodes = [bsp.ProcessingMode(self.calcangles, 'ev')]


class GreatCircleCalcBlock(bsp.BaseProcessor):
    def __init__(self, vincentydist):
        self.children = []
        self.vincentydist = vincentydist

    def triangulate(self, inevents):
        for event in inevents:
            dataarr = self.anglelocarr(event)
            for data in dataarr:
                obs = data['obs']
                angle = data['ang']
                data["circle"] = self.calccircle(angle, obs.file.location.latitude, obs.file.location.longitude)
            if len(dataarr) >= 2:
                #TODO logic to find two most propable obs
                event.pos_loc_lat, event.pos_loc_lon = self.resolveloc(dataarr[2], dataarr[0])
            if len(dataarr) >= 3:
                #self.thrdpointresolve(event, dataarr[2])
                pass
        return inevents

    def calccircle(self, ang, lat, lon):
        inip = gp.Point(lat, lon)
        target = VincentyDistance(kilometers=self.vincentydist).destination(inip, np.degrees(ang))
        cartesianinip = common.tocartesianyxz(lon=np.radians(inip.longitude), lat=np.radians(inip.latitude))
        cartesiantarget = common.tocartesianyxz(lon=np.radians(target.longitude), lat=np.radians(target.latitude))
        return np.cross(cartesianinip, cartesiantarget)

    def intersec(self, first, second):
        line = np.cross(first, second);
        x1 = line / math.sqrt(np.power(line[0], 2) + np.power(line[1], 2) + np.power(line[2], 2))
        inter1 = gp.Point(latitude=np.degrees(np.arcsin(x1[2])),
                          longitude=np.degrees(np.arctan2(x1[1], x1[0])))
        inter2 = gp.Point(latitude=np.degrees(np.arcsin(-x1[2])),
                          longitude=np.degrees(np.arctan2(-x1[1], -x1[0])))
        return inter1, inter2

    def resolveloc(self, first, second):
        pos1, pos2 = self.intersec(first['circle'], second['circle'])
        firstslarger = first['obs'].getpwr() > second['obs'].getpwr()
        p1 = first['obs'].file.location.getpoint()
        p2 = second['obs'].file.location.getpoint()
        firstcloser = VincentyDistance(p1, pos1).miles < VincentyDistance(p2, pos1).miles
        if (firstcloser and firstslarger) or (not firstcloser and not firstslarger):
            output = pos1
        else:
            output = pos2
        return output.latitude, output.longitude

    def thrdpointresolve(self,event, dataarr):
        negcircle = dataarr['ncircle']
        poscircle = dataarr['pcircle']
        negpoint = common.tocartesianyxz(event.neg_loc_lon, event.neg_loc_lat)
        pospoint = common.tocartesianyxz(event.pos_loc_lon, event.pos_loc_lat)

        if self.pointfromcircledist(negpoint, negcircle) > self.pointfromcircledist(pospoint, poscircle):
            event.polarity = 1
            #event.neg_loc_lat = None
            #event.neg_loc_lon = None
        else:
            event.polarity = 0
            #event.pos_loc_lat = None
            #event.pos_loc_lon = None

    def pointfromcircledist(self, point, circle):
        dotprod = np.dot(point, circle)
        angle = np.arccos(dotprod)
        return angle

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

    def children(self):
        return self._children

    def prcmodes(self):
        return self._prcmodes

    def __init__(self, vincentydist):
        self._children = []
        self.vincentydist = vincentydist
        self._prcmodes = [bsp.ProcessingMode(self.triangulate, 'ev')]








