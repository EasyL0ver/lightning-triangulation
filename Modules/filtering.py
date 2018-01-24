from scipy import signal
from pylab import *

from Modules import linelement as bsp
from Data import converter


class LPFilter(bsp.BaseProcessor):
    def flt(self, data):
        return signal.convolve(data, self.filter, mode='same')

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def __init__(self, cutoff, taps, window):
        self.filter = signal.firwin(taps, window=window, cutoff=cutoff)
        self._children = [];
        self._prcmodes = [bsp.ProcessingMode(self.flt, 'sn', toname='sn'), bsp.ProcessingMode(self.flt, 'ew')]


class HPFilter(LPFilter):
    def __init__(self, cutoff, taps, window):
        super(HPFilter, self).__init__(cutoff, taps, window)
        self.filter = - self.filter
        self.filter[taps / 2] = self.filter[taps / 2] + 1


class MovingAverageFilter(LPFilter):
    def __init__(self, taps):
        self.filter = np.ones(taps).astype(float)/taps
        self._children = [];
        self._prcmodes = [bsp.ProcessingMode(self.flt, 'sn', toname='sn'), bsp.ProcessingMode(self.flt, 'ew')]


class DeconvolutionBlock(bsp.BaseProcessor):
    def flt(self, data):
        if self.enabled:
            return self.deconvolute(data, self.mask)
        return  data

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def deconvolute(self, g, f):
        np.seterr(over='raise')
        lf = len(f)
        lg = len(g)
        h = np.zeros(lg - lf + 1)
        for n in range(0, len(h)):
            h[n] = g[n]
            # prevent negative index
            for i in range(max(n - lf + 1, 0), n):
                h[n] -= h[i] * f[n - i]
        return h

    def conjugate(self, mask):
        l = len(mask) + 1
        j = 1
        for i in range(l/2, l-1):
            mask[i] = np.conj(mask[l/2 - j])
            j += 1

    def __init__(self, mask_source, enabled):
        self.mask_freq, self.maskh = converter.convert_deconvolution_mask(mask_source)
        self.conjugate(self.maskh)
        self.mask = np.fft.ifft(self.maskh)
        self.mask = np.real(self.mask)
        #figure(1)
        #plot(np.imag(self.mask))
        #plot(np.real(self.mask))
        #show()
        self.mask = np.real(self.mask)

        self.enabled = enabled
        self._children = [];
        self._prcmodes = [bsp.ProcessingMode(self.flt, 'sn', toname='sn'),
                          bsp.ProcessingMode(self.flt, 'ew')]


class ResamplingFFTDeconvolution(bsp.BaseProcessor):
    def flt(self, data):
        data_transform = np.fft.fft(data)
        figure(1)
        plot(np.imag(data_transform))
        plot(np.real(data_transform))
        show()
        if len(data_transform) != self.expected_length:
            print("skaszanilo sie :/")
            return
        for i in range(0, len(data)):
            data_transform[i] = data_transform[i] / self.resampled_mask_h[i]
            c = 1
        figure(1)
        plot(np.imag(data_transform))
        plot(np.real(data_transform))
        show()
        output = np.fft.ifft(data_transform)
        norm_factor = max(data)/max(output)
        return np.real(output) * norm_factor

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def conjugate(self, mask):
        l = len(mask) + 1
        j = 1
        for i in range(l/2, l-1):
            mask[i] = np.conj(mask[l/2 - j])
            j += 1

    def __init__(self, mask_source, expected_length):
        self.mask_freq, self.maskh = converter.convert_deconvolution_mask(mask_source)
        self.conjugate(self.maskh)
        self.expected_length = expected_length
        self.resampled_mask_h = signal.resample(self.maskh, self.expected_length) * 500

        figure(1)
        plot(self.resampled_mask_h)
        show()

        self._children = [];
        #self._prcmodes = [bsp.ProcessingMode(self.flt, 'sn', toname='sn'),
        #                  bsp.ProcessingMode(self.flt, 'ew')]
        self._prcmodes = [bsp.ProcessingMode(self.flt, 'sn', toname='dec')]


class BandStopFilter(bsp.BaseProcessor):
    def flt(self, data):
        # mfreqz(self.filter)
        return signal.convolve(data, self.filter, mode='same')

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def __init__(self, band, bandwidth, taps):
        f1 = band - bandwidth
        f2 = band + bandwidth
        if f1 < 0.01:
            f1 = 0.01
        if f2 > 0.99:
            f2 = 0.99
        self.filter = signal.firwin(taps, [f1, f2])
        self._children = []
        self._prcmodes = [bsp.ProcessingMode(self.flt, 'sn'), bsp.ProcessingMode(self.flt, 'ew')]


class IIRNotchFilter(bsp.BaseProcessor):
    def flt(self, data):
        return signal.filtfilt(self.filter_a, self.filter_b, data)

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def __init__(self, band, taps):
        self.filter_a, self.filter_b = signal.iirnotch(band, taps)
        self._children = []
        self._prcmodes = [bsp.ProcessingMode(self.flt, 'sn'), bsp.ProcessingMode(self.flt, 'ew')]


class HilbertEnvelopeBlock(bsp.BaseProcessor):
    def calc_envelope(self, data):
        return np.abs(signal.hilbert(data))

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def __init__(self, parameter):
        self._children = [];
        self._prcmodes = [bsp.ProcessingMode(self.calc_envelope, parameter, toname='env')]


class RegionBasedBandStop(bsp.BaseProcessor):
    def region_filter(self, vector, file):
        if not file.location.reqionfreq:
            return vector
        frequency = float(file.location.reqionfreq)/float(file.fsample/2)
        if frequency not in self.filter_dictionary:
            if self.mode == 'iir':
                self.filter_dictionary[frequency] = IIRNotchFilter(frequency, self.taps)
            else:
                self.filter_dictionary[frequency] = BandStopFilter(frequency, self.bandwidth, self.taps)

        bandstop = self.filter_dictionary[frequency]
        return bandstop.flt(vector)

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def __init__(self, bandwidth, taps, mode=None):
        self.filter_dictionary = dict()
        self._children = []
        self.mode = mode
        self.bandwidth = bandwidth
        self.taps = taps
        self._prcmodes = [bsp.ProcessingMode(self.region_filter, 'ew', 'file'),
                          bsp.ProcessingMode(self.region_filter, 'sn', 'file')]


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






