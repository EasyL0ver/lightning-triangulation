from pylab import *
import scipy.signal as signal
import baseprocessor as bsp


class ConversionError(object):
    def __init__(self):
        self.conversionSucces = True
        self.conversionErrorLog = "Wszystko spoko!"

    def reportFailure(self, errorlog):
        self.conversionSucces = False
        self.conversionErrorLog = errorlog


class DataStruct(object):
    def __init__(self, data, initTime, timelen, fsample, date, time, location, headerhash):
        self.data = data
        self.initTime = initTime
        self.timelen = timelen
        self.fsample = fsample
        self.date = date
        self.time = time
        self.location = location
        self.headerhash = headerhash

class TestPlotBlock(bsp.BaseProcessor):
    def __init__(self, figuren, plot):
        self.figuren = figuren
        self.plot = plot

    def process(self, data):
        self.data = data
        if self.plot == True:
            figure(self.figuren)
            plot(data)
            show()
        if self.plot == False:
            print(data)

    def getChildren(self):
        return


def mfreqz(b,a=1):
    w,h = signal.freqz(b,a)
    h_dB = 20 * log10 (abs(h))
    subplot(211)
    plot(w/max(w),h_dB)
    ylim(-150, 5)
    ylabel('Magnitude (db)')
    xlabel(r'Normalized Frequency (x$\pi$rad/sample)')
    title(r'Frequency response')
    subplot(212)
    h_Phase = unwrap(arctan2(imag(h),real(h)))
    plot(w/max(w),h_Phase)
    ylabel('Phase (radians)')
    xlabel(r'Normalized Frequency (x$\pi$rad/sample)')
    title(r'Phase response')
    subplots_adjust(hspace=0.5)