import copy
import datetime as dt

import numpy as np

import linelement
from Data import datamodels as dm, common
from Modules import linelement as bsp


class EntityToDbEndpoint(linelement.BaseProcessor):
    def db_add(self, events):
        for event in events:
            self.orm.get_session().add(event)

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def __init__(self, dprovider, type):
        self.orm = dprovider.orm_provider
        self._children = None
        self._prcmodes = [bsp.ProcessingMode(self.db_add, type)]

    def flush(self):
        self.orm.get_session().commit()


class LocalMaximumEventBlock(linelement.BaseProcessor):
    def calc_events(self, cluster_data, signal, signal2, infile, power_threshold):
        events = []
        for cluster in cluster_data:
            local_max = np.argmax(power_threshold[cluster['start']:cluster['end'] + 1]) + cluster['start']
            max_power = min((power_threshold[local_max] / self.crttresh) * 100, 100)
            event_start = local_max - self.prelen
            event_end = local_max + self.postlen
            if event_start < 0:
                event_start = 0
            if event_end > len(signal) - 1:
                event_end = len(signal) - 1
            events.append(dm.Observation(firstsample=event_start, samplelen=event_end - event_start,
                                         file_id=infile.id, event_type='basic_event',
                                         sample=local_max, sn_max_value=signal[local_max],
                                         ew_max_value=signal2[local_max], certain=max_power))
            infile.events_created = 1
        return events

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def __init__(self, prelen, postlen, crttresh):
        self._children = []
        self.prelen = prelen
        self.postlen = postlen
        self.crttresh = crttresh
        self._prcmodes = [bsp.ProcessingMode(self.calc_events, 'clstr_th', 'sn', 'ew', 'file', 'pwr_th', toname='obs')]


class TimeOffsetObservationConnectorBlock(linelement.BaseProcessor):
    # groups observations together based on time offset
    # performance bottleneck here, crucial to optimize
    def connect(self, observations):
        if len(observations) <= 1:
            print("Single observation provided, aborting")
            return
        unique_locations = set([observation.file.location.name for observation in observations])
        if len(unique_locations) == 0:
            print("No Locations provided")
            return
        events = []
        for location in unique_locations:
            for first_observation in observations:
                if first_observation.assigned_event:
                    continue
                if first_observation.file.location.name == location:
                    # if base observation certainty below treshold skip this one
                    if first_observation.certain < self.crttresh:
                        continue
                    locations_left = copy.deepcopy(unique_locations)
                    locations_left.remove(location)
                    event = dm.Event(obs1_id=first_observation.id)
                    first_observation.assigned_event = event
                    # combine date and time for comparison
                    first_date_time = common.cmbdt(first_observation.file.date, first_observation.file.time) + dt.timedelta(
                        seconds=float(first_observation.sample) / first_observation.file.fsample)
                    positions_dictionary = dict()
                    for l in locations_left:
                        positions_dictionary[l] = []
                    # iterate through observations in different location to find matching one
                    for second_observation in observations:
                        if second_observation.assigned_event:
                            continue
                        if len(locations_left) == 0:
                            break
                        if second_observation.file.location.name in locations_left:
                            # check if within timedelta
                            second_date_time = common.cmbdt(second_observation.file.date, second_observation.file.time) + \
                                               dt.timedelta(seconds=float(second_observation.sample) / second_observation.file.fsample)
                            if first_date_time - self.timedelta < second_date_time < first_date_time + self.timedelta:
                                positions_dictionary[second_observation.file.location.name].append(second_observation)
                    # append observation with max certainty
                    for key in positions_dictionary:
                        arr = positions_dictionary[key]
                        max_certainty = 0
                        output = None
                        for obs in arr:
                            if obs.certain > max_certainty:
                                max_certainty = obs.certain
                                output = obs
                        if output is not None:
                            if event.obs2 is None:
                                event.obs2 = output
                                output.assigned_event = event
                            else:
                                event.obs3 = output
                                output.assigned_event = event

                    events.append(event)
        return events

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def __init__(self, timedelta, crttresh):
        self._children = []
        self.timedelta = timedelta
        self.crttresh = crttresh
        self._prcmodes = [bsp.ProcessingMode(self.connect, 'obs', toname='ev')]
