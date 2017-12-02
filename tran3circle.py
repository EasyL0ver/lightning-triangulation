import numpy as np
import common
import geopy as gp
from geopy.distance import VincentyDistance

inlatitude = 45.012
inlongitude = 121.16
arrivalrad = 90
kmdelta = 1000

inip = gp.Point(45, 45)
postarget = VincentyDistance(kilometers=1000).destination(inip, 0)
negtarget = VincentyDistance(kilometers=1000).destination(inip, 180)
var = 1




var = 1