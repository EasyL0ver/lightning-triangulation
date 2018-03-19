from motionless import CenterMap
from motionless import LatLonMarker, DecoratedMap
import urllib2
import matplotlib.pyplot as plt

cmap = DecoratedMap(lat=1.1, lon=18.6, zoom=4, size_x=640, size_y=440)
cmap.add_marker(LatLonMarker(1.1, 18.6, color='red', size='mid'))
cot = cmap.generate_url()

req = urllib2.Request(cot, headers={'User-Agent' : "Magic Browser"})
con = urllib2.urlopen(req)

a = plt.imread(con)
plt.imshow(a)
plt.show()


print(range(0, 4))