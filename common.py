from pylab import *
import scipy.signal as signal

class ConversionError:
    def __init__(self):
        self.conversionSucces = True
        self.conversionErrorLog = "Wszystko spoko!"

    def reportFailure(self, errorlog):
        self.conversionSucces = False
        self.conversionErrorLog = errorlog

class DataStruct:
    def __init__(self,data,initTime,headerString):
        self.data = data
        self.initTime = initTime
        self.headerString = headerString


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