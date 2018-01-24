import itertools as it
import math

import geopy as gp
import numpy as np
from geopy.distance import VincentyDistance

from Modules import linelement as bsp
from Data import common


class AngleCalcBlock(bsp.BaseProcessor):
    def calculate_angles(self, input_events):
        #assert events data
        for event in input_events:
            if event.obs1_id:
                event.ob1_angle = self.calcangle(event.obs1)
            if event.obs2_id:
                event.ob2_angle = self.calcangle(event.obs2)
            if event.obs3_id:
                event.ob3_angle = self.calcangle(event.obs3)
        return input_events

    def calcangle(self, input_observation):
        #TODO ostateczna wersja tego here
        rad = math.pi / 2 - math.atan(input_observation.ew_max_value / input_observation.sn_max_value)
        return rad

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def __init__(self):
        self._children = []
        self._prcmodes = [bsp.ProcessingMode(self.calculate_angles, 'ev')]


class GreatCircleCalcBlock(bsp.BaseProcessor):
    def __init__(self, vincenty):
        self.children = []
        self.vincenty_distance = vincenty

    def triangulate(self, input_events):
        for event in input_events:
            triangulation_data = event.get_angles_locations()
            for data in triangulation_data:
                obs = data['obs']
                angle = data['ang']
                data["circle"] = self.calculate_circle(angle, obs.file.location.latitude, obs.file.location.longitude)

            triangulation_data = sorted(triangulation_data, key=lambda x: x['obs'].certain, reverse=True)

            if len(triangulation_data) >= 2:
                points = []
                for subset in it.combinations(triangulation_data, 2):
                    lat, lon = self.resolve_location(subset[0], subset[1])
                    certainty = min(subset[0]['obs'].certain, subset[1]['obs'].certain)
                    points.append({'lat': lat, 'lon': lon, 'cert': certainty})

                event.loc_lat, event.loc_lon = self.location_mean(points)

        return input_events

    def calculate_circle(self, ang, lat, lon):
        initial_point = gp.Point(lat, lon)
        target = VincentyDistance(kilometers=self.vincenty_distance).destination(initial_point, np.degrees(ang))
        cartesian_initial = common.tocartesianyxz(lon=np.radians(initial_point.longitude), lat=np.radians(initial_point.latitude))
        cartesian_target = common.tocartesianyxz(lon=np.radians(target.longitude), lat=np.radians(target.latitude))
        return np.cross(cartesian_initial, cartesian_target)

    def intersect(self, first, second):
        line = np.cross(first, second);
        x1 = line / math.sqrt(np.power(line[0], 2) + np.power(line[1], 2) + np.power(line[2], 2))
        inter1 = gp.Point(latitude=np.degrees(np.arcsin(x1[2])),
                          longitude=np.degrees(np.arctan2(x1[1], x1[0])))
        inter2 = gp.Point(latitude=np.degrees(np.arcsin(-x1[2])),
                          longitude=np.degrees(np.arctan2(-x1[1], -x1[0])))
        return inter1, inter2

    def resolve_location(self, first, second):
        pos1, pos2 = self.intersect(first['circle'], second['circle'])
        first_larger = first['obs'].getpwr() > second['obs'].getpwr()
        p1 = first['obs'].file.location.getpoint()
        p2 = second['obs'].file.location.getpoint()
        first_closer = VincentyDistance(p1, pos1).miles < VincentyDistance(p2, pos1).miles
        if (first_closer and first_larger) or (not first_closer and not first_larger):
            output = pos1
        else:
            output = pos2
        return output.latitude, output.longitude

    def location_mean(self, points):
        output_lon = 0
        output_lat = 0
        cert_sum = 0
        for point in points:
            cert_sum += point['cert']
            output_lat += point['lat'] * point['cert']
            output_lon += point['lon'] * point['cert']

        return output_lon/cert_sum, output_lat/cert_sum

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def __init__(self, vincentydist):
        self._children = []
        self.vincenty_distance = vincentydist
        self._prcmodes = [bsp.ProcessingMode(self.triangulate, 'ev')]








