#-*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from Modules import linelement as bsp
import datetime as dt
import numpy as np


class BaseAsyncPlotBlock(bsp.BaseProcessor):
    def on_enter(self, dbus):
        plt.figure(self.figuren)
        super(BaseAsyncPlotBlock, self).on_enter(dbus)

    def plt(self, data):
        if data is not None:
            plt.plot(data)

    def push_data(self, data):
        if self.pltsetting:
            plt.show()
        super(BaseAsyncPlotBlock, self).push_data(data)

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def __init__(self, figuren, pltsetting, *plots):
        self.figuren = figuren
        self._children = []
        self._prcmodes = []
        self.pltsetting = pltsetting
        for pl in plots:
            self._prcmodes.append(bsp.ProcessingMode(self.plt, pl))


class FftPlotBlock(BaseAsyncPlotBlock):
    def plt(self, data):
        if data is not None:
            n = len(data)
            k = np.arange(n)
            T = n / 887.7840909
            frq = k / T
            frq = frq[range(n / 2)]

            Y = np.fft.fft(data) / n
            Y = Y[range(n / 2)]
            plt.plot(frq, abs(Y), 'r')
            plt.xlabel(u'Częstotliwość [Hz]')
            plt.ylabel(u'Amplituda [pT]')


class ObservationPlotBlock(BaseAsyncPlotBlock):
    def plt(self, observation, sn_data, ew_data):
        time = dt.datetime.combine(observation.file.date, observation.file.time)
        time += dt.timedelta(seconds=float(observation.firstsample)/observation.file.fsample)

        span = np.arange(len(sn_data)).astype(float) / observation.file.fsample
        plt.title("Datetime: " + str(time) + " Location: " + observation.file.location.name)
        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude [pT]")
        plt.plot(span, sn_data)
        plt.plot(span, ew_data)

    def __init__(self):
        self.figuren = 1
        self.pltsetting = True
        self._children = []
        self._prcmodes = []
        self._prcmodes.append(bsp.ProcessingMode(self.plt, 'obs_single', 'sn', 'ew'))
