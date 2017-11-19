from pylab import *
import scipy.signal as signal
import baseprocessor as bsp
import io
import sqlite3
import datetime as dt

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
        self.children = None

    def process(self, data):
        self.data = data
        if self.plot == True:
            figure(self.figuren)
            plot(data)
            show()
        if self.plot == False:
            print(data)


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

def binarytonp(binary):
    # use a compressor here
    out = io.BytesIO(binary)
    out.seek(0)
    return np.load(out)

def nptobinary(npdata):
    out = io.BytesIO()
    np.save(out, npdata)
    out.seek(0)
    return sqlite3.Binary(out.read())

def cmbdt(date,time):
    return dt.datetime.combine(date, time)
