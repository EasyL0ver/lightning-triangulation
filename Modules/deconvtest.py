import numpy as np


def deconv(g, f):
    lf = len(f)
    lg = len(g)
    h = np.zeros(lg - lf + 1)
    for n in range(0, len(h)):
        h[n] = g[n];
        #prevent negative index
        for i in range(max(n - lf + 1, 0), n):
            h[n] -= h[i] * f[n-i]
        h[n] = h[n] / f[0];
    return h


h = [-8,-9,-3,-1,-6,7]
f = [-3,-6,-1,8,-6,3,-1,-9,-9,3,-2,5,2,-2,-7,-1]
g = [24,75,71,-34,3,22,-45,23,245,25,52,25,-67,-96,96,31,55,36,29,-43,-7]


chalo = deconv(g, f)
var = 1