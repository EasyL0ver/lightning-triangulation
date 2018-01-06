import linelement as bsp
import scipy.signal as signal
import numpy as np


class ThresholdBlock(bsp.BaseProcessor):
    def power_threshold(self, d1):
        output_values = np.zeros(len(d1))
        for i in range(0, len(d1)):
            if d1[i] >= self.thresh:
                output_values[i] = d1[i] - self.thresh
            else:
                output_values[i] = 0

        return output_values

    def children(self):
        return self._children

    def prcmodes(self):
        return self._prcmodes

    def __init__(self, thresh, threshold_value, values):
        self.thresh = thresh
        self.threshold_value = threshold_value
        self._children = []
        self._prcmodes = [bsp.ProcessingMode(self.power_threshold, values, toname='pwr_th')]


class PowerBlock(bsp.BaseProcessor):
    def power(self, d1, d2):
        if len(d1) != len(d2):
            print(self.tostring() + " vector lenghts don't match")
            return
        output_values = np.zeros(len(d1))
        for i in range(0, len(d1)):
            output_values[i] = np.sqrt(np.power(d1[i], 2) + np.power(d2[i], 2))
        return output_values

    def children(self):
        return self._children

    def prcmodes(self):
        return self._prcmodes

    def __init__(self):
        self._children = []
        self._prcmodes = [bsp.ProcessingMode(self.power, 'sn', 'ew', toname='pwr')]


class ThresholdClusterFilter(object):
    pass


class ThresholdClusterBlock(bsp.BaseProcessor):
    def cluster_thresholds(self, thresholds):
        #find fixed len event by local maxima
        is_state_high = False
        event_ranges = []

        release_counter = 0;
        if thresholds[0] > 0:
            is_state_high = True
            event_ranges.append({'start': 0, 'end': None})
            release_counter = self.deadlen

        for i in range(1, len(thresholds)-1):
            if thresholds[i] > 0:
                release_counter = self.deadlen
                if thresholds[i-1] == 0 and not is_state_high:
                    event_ranges.append({'start': i, 'end': None})
                    is_state_high = True
            if thresholds[i] == 0 and is_state_high and release_counter <= 0:
                event_ranges[len(event_ranges)-1]['end'] = i
                is_state_high = False
            release_counter -= 1

        if is_state_high:
            event_ranges[len(event_ranges)-1]['end'] = len(thresholds)
        if not is_state_high and thresholds[len(thresholds)-1] == 1:
            event_ranges.append({'start': len(thresholds) - 1, 'end': len(thresholds) - 1})

        return event_ranges

    def children(self):
        return self._children

    def prcmodes(self):
        return self._prcmodes

    def __init__(self, deadlen):
        self._children = []
        self.deadlen = deadlen
        self._prcmodes = [bsp.ProcessingMode(self.cluster_thresholds, 'pwr_th', toname='clstr_th')]










