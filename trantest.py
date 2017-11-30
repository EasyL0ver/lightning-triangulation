import common
import math
from geopy.distance import VincentyDistance
import geopy
import numpy as np


def to_radians(theta):
    return np.divide(np.dot(theta, np.pi), np.float32(180.0))

def to_degrees(theta):
        return np.divide(np.dot(theta, np.float32(180.0)), np.pi)


inlatitude = 45.012
inlongitude = 121.16
theta = 1.1
delta = np.float64(1000)/np.float64(12742)





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

    lat2 = np.arcsin( np.sin(lat1) * np.cos(delta) +
                      np.cos(lat1) * np.sin(delta) * np.cos(theta) )

    lng2 = lon1 + np.arctan2( np.sin(theta) * np.sin(delta) * np.cos(lat1),
                              np.cos(delta) - np.sin(lat1) * np.sin(lat2))

    lng2 = (lng2 + 3 * np.pi) % (2 * np.pi) - np.pi

    newc = common.SphericalCoordinate()
    newc.latitude = to_degrees(lat2)
    newc.longitude= to_degrees(lng2)

    cords.append(newc)

    i = i + 1
    if i > 500:
        distanceclose = True




var = 1










