import math

import numpy as np

from Data import common


def to_radians(theta):
    return np.divide(np.dot(theta, np.pi), np.float32(180.0))

def to_degrees(theta):
        return np.divide(np.dot(theta, np.float32(180.0)), np.pi)


inlatitude = 45.012
inlongitude = 121.16
theta = -0.00548016
delta = np.float64(1000)/np.float64(12742)
meterdelta = 1000000





sphcord = common.SphericalCoordinate()
sphcord.latitude = inlatitude
sphcord.longitude = inlongitude

distanceclose = False
cords = []
cords.append(sphcord)
i = 1


while not distanceclose:
    lati = cords[i - 1].latitude
    loni = cords[i - 1].longitude

    lat1 = to_radians(lati)
    lon1 = to_radians(loni)
    #origin = geopy.Point(lati,loni)
    #output = VincentyDistance(kilometers=100).destination(origin, theta)
    newc = common.SphericalCoordinate()


    north = meterdelta * math.cos(theta) / 111111
    east = meterdelta * math.sin(theta) / math.cos(lat1) / 111111

    newc.latitude = lati + north
    newc.longitude= loni + east

    cords.append(newc)

    i = i + 1
    if i > 50:
        distanceclose = True




var = 1










