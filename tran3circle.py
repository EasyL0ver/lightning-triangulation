import numpy as np
import common
import geopy as gp
from geopy.distance import VincentyDistance

inlatitude = 45.012
inlongitude = 121.16
arrivalrad = 90
kmdelta = 1000





inip = gp.Point(inlatitude, inlongitude)
target = VincentyDistance(kilometers=kmdelta).destination(inip, arrivalrad)




    var = 1