#-*- coding: utf-8 -*-

import scipy.signal as signal
import numpy as np
from pylab import *


def mfreqz(b,a=1):
    w,h = signal.freqz(b,a)
    h_dB = 20 * log10 (abs(h))
    plot(w/max(w),h_dB)
    return w/max(w), h_dB


n1 = 5
n2 = 20
n3 = 50

f1 = np.ones(n1).astype(float)/n1
f2 = np.ones(n2).astype(float)/n2
f3 = np.ones(n3).astype(float)/n3

x, y = mfreqz(f1)
plot(x, y, label="n = 5")

x, y = mfreqz(f2)
plot(x, y, label="n = 20")

x, y = mfreqz(f3)
plot(x, y, label="n = 50")

xlim([0,0.5])
ylabel('Amplituda [dB]')
xlabel(u'Znormalizowana częstotliwość [x$\pi$rad/próbka]')


legend()
show()
