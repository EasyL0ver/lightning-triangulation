#-*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from Modules import linelement as bsp
import datetime as dt
import numpy as np
from matplotlib import gridspec
import mpl_toolkits.basemap as map


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
        plt.title("Datetime: " + str(time) + " Location: " + observation.file.location.name + " Cert:" + str(observation.certain))
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


class FilePlotBlock(BaseAsyncPlotBlock):
    def plt(self, file):
        time = dt.datetime.combine(file.date, file.time)
        data = file.load_data()
        sn_data = data['sn']
        ew_data = data['ew']

        span = np.arange(len(sn_data)).astype(float) / file.fsample
        plt.title("Datetime: " + str(time) + " Location: " + file.location.name )
        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude [pT]")
        plt.plot(span, sn_data)
        plt.plot(span, ew_data)

    def __init__(self):
        self.figuren = 1
        self.pltsetting = True
        self._children = []
        self._prcmodes = []
        self._prcmodes.append(bsp.ProcessingMode(self.plt, 'file'))


class EventPlotBlock(BaseAsyncPlotBlock):
    def plt(self, event):
        # decide on displayed data length
        location_available = event.loc_lon is not None
        location_available = False

        starttimes = []
        endtimes = []
        self.write_times(event.obs1, starttimes, endtimes)
        self.write_times(event.obs2, starttimes, endtimes)
        self.write_times(event.obs3, starttimes, endtimes)

        plot_time_start = min(starttimes)
        plot_time_end = max(endtimes)

        plotdata=[]
        self.write_plot_data(event.obs1, plotdata, plot_time_start, plot_time_end)
        self.write_plot_data(event.obs2, plotdata, plot_time_start, plot_time_end)
        self.write_plot_data(event.obs3, plotdata, plot_time_start, plot_time_end)

        if self.dsp:
            for plot in plotdata:
                self.dsp.on_enter(plot['data'])
                plot['data'] = self.cache.cachedData
                self.cache.clear()

        # ymax, ymin = self.resolve_limits(plotdata)

        # select layout
        gs = None
        gs_len = 0
        if location_available and len(plotdata) == 3:
            gs = gridspec.GridSpec(4, 1, height_ratios=[3, 1, 1, 1])
            gs_len = 4
        elif location_available and len(plotdata) == 2:
            gs = gridspec.GridSpec(3, 1, height_ratios=[2, 1, 1])
            gs_len = 3
        else:
            gs = gridspec.GridSpec(len(plotdata), 1, height_ratios=np.ones(len(plotdata)))
            gs_len = len(plotdata)

        plt.tight_layout()
        plot_data_index = 0
        for i in range(0, gs_len):
            if location_available and i == 0:
                #plotuje swiat
                ax = plt.subplot(gs[i])
                map = mp.Basemap(projection='merc',ax=ax)
                map.drawcoastlines()
                map.drawcountries()
                map.fillcontinents(color='coral')
                map.drawmapboundary()

                continue
            ax = plt.subplot(gs[i])
            data_bus = plotdata[i]['data']
            span = np.arange(len(data_bus['sn'])).astype(float) / plotdata[i]['obs'].file.fsample
            ax.plot(span, data_bus['sn'])
            ax.plot(span, data_bus['ew'])
            ax.set_ylabel("Amplitude [pT]")
            ax.text(0.9, 0.95, plotdata[i]['label'],
                 horizontalalignment='center',
                 verticalalignment='center',
                 transform=ax.transAxes)
            plot_data_index += 1

            if i == gs_len - 1:
                ax.set_xlabel("Time [s]")

        var = 1

    def write_times(self, observation, starttimes, endtimes):
        if observation:
            start_time = dt.datetime.combine(observation.file.date, observation.file.time)
            start_time += dt.timedelta(seconds=float(observation.firstsample)/observation.file.fsample)
            end_time = start_time + dt.timedelta(seconds=float(observation.samplelen)/observation.file.fsample)
            starttimes.append(start_time)
            endtimes.append(end_time)

    def write_plot_data(self, observation, collection, plot_time_start, plot_time_end):
        if observation:
            plot_data = dict()
            plot_data['label'] = observation.file.location.name
            plot_data['data'] = observation.file.load_range(plot_time_start, plot_time_end)
            plot_data['obs'] = observation
            collection.append(plot_data)

    def resolve_limits(self, plotdata):
        max_val = 0
        min_val = 0
        for entry in plotdata:
            data = entry['data']
            ma = max(max(data['sn']), max(data['ew']))
            mi = max(min(data['sn']), min(data['ew']))

            if mi < min_val:
                min_val = mi
            if ma > max_val:
                max_val = ma

        return min_val, max_val




    def __init__(self, dsp_template_instance = None):
        self.figuren = 1
        self.pltsetting = True
        self.cache = None
        self.dsp = dsp_template_instance
        self._children = []
        self._prcmodes = []
        self._prcmodes.append(bsp.ProcessingMode(self.plt, 'ev_single'))

        if self.dsp:
            self.cache = bsp.MemoryBlock()
            self.dsp.children().append(self.cache)

