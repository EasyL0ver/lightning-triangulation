#-*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from scipy import signal
from Modules import linelement as bsp
from Data import datamodels
import datetime as dt
import numpy as np
from matplotlib import gridspec


class BaseAsyncPlotBlock(bsp.BaseProcessor):
    def on_enter(self, dbus):
        self.figure = plt.figure(self.figuren)
        super(BaseAsyncPlotBlock, self).on_enter(dbus)

    def plt(self, data):
        if data is not None:
            #tymaczowo
            span = np.arange(len(data)).astype(float) / 887
            plt.xlabel(u"Czas [s]")
            plt.ylabel(u"Moduł wektora amplitudy [|pT|]")
            plt.plot(span, data)

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
        self.figure = None
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
            #plt.semilogy(frq, abs(Y), 'r')
            #plt.xlabel(u'Częstotliwość [Hz]')
            #plt.ylabel(u'Amplituda [pT]')

            f, Pxx_den = signal.periodogram(data, 887.7840909, window="hamming", scaling="spectrum")
            plt.semilogy(f, Pxx_den)
            plt.xlabel(u'Częstotliwość [Hz]')
            plt.ylabel(u'Amplitudowa gęstośc spektralna [pT^2/Hz]')
            plt.ylim([10**-7, 10**7])
            plt.xlim([0, 200])
            plt.show()

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


class ObservationPlotBlock(BaseAsyncPlotBlock):
    def plt(self, observation, sn_data, ew_data):
        time = dt.datetime.combine(observation.file.date, observation.file.time)
        time += dt.timedelta(seconds=float(observation.firstsample)/observation.file.fsample)

        span = np.arange(len(sn_data)).astype(float) / observation.file.fsample
        plt.title("Datetime: " + str(time) + " Location: " + observation.file.location.name + " Cert:" + str(observation.certain))
        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude [pT]")
        plt.plot(span, sn_data)
        obs_time = (float(observation.sample) - float(observation.firstsample))/observation.file.fsample
        plt.axvline(x=obs_time, color='g', linestyle='dashed', alpha=0.5)


    def __init__(self):
        self.figuren = 1
        self.pltsetting = True
        self._children = []
        self._prcmodes = []
        self._prcmodes.append(bsp.ProcessingMode(self.plt, 'obs_single', 'sn', 'ew'))


class FilePlotBlock(BaseAsyncPlotBlock):
    def plt(self, file, sn, ew):
        time = dt.datetime.combine(file.date, file.time)
        data = file.load_data()
        sn_data = sn
        ew_data = ew

        if self.mode == 'fft':
            #f, Pxx_den = signal.periodogram(sn_data, 887.7840909, window="hamming")
            f, Pxx_den = signal.welch(sn_data, 887.7840909, nperseg=4096)
            plt.semilogy(f, Pxx_den)
            plt.title("Datetime: " + str(time) + " Location: " + file.location.name)
            plt.xlabel(u'Częstotliwość [Hz]')
            plt.ylabel(u'Amplitudowa gęstośc spektralna [pT^2/Hz]')
            plt.ylim([10**-4, 10**5])
            plt.xlim([0, 200])
        else:
            span = np.arange(len(sn_data)).astype(float) / file.fsample
            plt.title("Datetime: " + str(time) + " Location: " + file.location.name )
            plt.xlabel("Time [s]")
            plt.ylabel("Amplitude [pT]")
            plt.plot(span, sn_data)
            plt.plot(span, ew_data)

            #todo change this to collection relations in the future
            if self.dataprovider:
                observations_in_file = self.dataprovider.orm_provider.get_session().\
                    query(datamodels.Observation).filter(datamodels.Observation.file_id == file.id).all()
                for observation in observations_in_file:
                    plt.axvline(x=(float(observation.sample)/file.fsample), color='g', linestyle='dashed', alpha=0.5)


    def __init__(self, mode=None, dataprovider=None):
        self.mode = mode
        self.dataprovider = dataprovider
        self.figuren = 1
        self.pltsetting = True
        self._children = []
        self._prcmodes = []
        self._prcmodes.append(bsp.ProcessingMode(self.plt, 'file', 'sn', 'ew'))


class FileClusterPlotBlock(FilePlotBlock):
    def on_enter(self, dbus):
        #self.figure = plt.figure(self.figuren)
        super(BaseAsyncPlotBlock, self).on_enter(dbus)

    def cluster_plot(self, cluster):
        self.figure, subplots = plt.subplots(len(cluster), 1, sharex=True, sharey=True)
        for i in range(0, len(cluster)):
            plt.axes(subplots[i])
            data = cluster[i].load_data()

            if self.dsp_instance:
                self.dsp_instance.on_enter(data)
                data = self.cache.cachedData
                self.cache.clear()

            self.plt(data['file'], data['sn'], data['ew'])

            if self.mode == "fft":
                plt.ylabel(" ")
            if i != len(cluster)-1:
                plt.xlabel(" ")
        pass


    def __init__(self, mode=None, dataprovider=None, dsp_template_instance=None):
        self.mode = mode
        self.dataprovider = dataprovider
        self.dsp_instance = dsp_template_instance
        self.figuren = 1
        self.pltsetting = True
        self._children = []
        self._prcmodes = []
        self._prcmodes.append(bsp.ProcessingMode(self.cluster_plot, 'file_cluster'))

        if self.dsp_instance:
            self.cache = bsp.MemoryBlock()
            self.dsp_instance.children().append(self.cache)


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

        plotdata = sorted(plotdata, key=lambda x: x['obs'].file.location.id)

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

        #plt.tight_layout()
        plot_data_index = 0
        for i in range(0, gs_len):
            if location_available and i == 0:
                #TODO PLOT MAP
                continue
            ax = plt.subplot(gs[i])
            data_bus = plotdata[i]['data']

            added_time_offest = plotdata[i]['obs'].get_start_time() - plot_time_start
            obs_time = (float(plotdata[i]['obs'].sample) - float(plotdata[i]['obs'].firstsample)) / plotdata[i]['obs'].file.fsample
            obs_time += added_time_offest.total_seconds()

            span = np.arange(len(data_bus['sn'])).astype(float) / plotdata[i]['obs'].file.fsample
            ax.plot(span, data_bus['sn'])
            ax.plot(span, data_bus['ew'])
            ax.set_ylabel("Amplitude [pT]")
            plt.axvline(x=obs_time, color='g', linestyle='dashed', alpha=0.5)
            ax.text(0.9, 0.95, plotdata[i]['label'],
                 horizontalalignment='center',
                 verticalalignment='center',
                 transform=ax.transAxes)
            plot_data_index += 1

            if i == 0:
                ax.set_title("Event located at Lon: " + str(event.loc_lon) +" Lat: " + str(event.loc_lat) + " Time: " + str(plot_time_start))
            if i == gs_len - 1:
                ax.set_xlabel("Time [s]")

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

