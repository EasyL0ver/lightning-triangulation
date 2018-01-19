from abc import ABCMeta, abstractmethod, abstractproperty
from datetime import datetime
import copy


class BaseProcessor:
    __metaclass__ = ABCMeta

    def on_enter(self, dbus):
        print("Current module " + self.to_string())
        processing_modes = self.processing_modes()
        for mode in processing_modes:
            tup = []
            for argument in mode.fromname:
                tup.append(dbus.data[argument])
            dbus.data[mode.toname] = mode.prcdelegate(*tup)
        dbus.modified = True
        dbus.datastring += " "
        dbus.datastring += self.to_string()
        self.push_data(dbus)

    @abstractproperty
    def processing_modes(self):
        pass

    @abstractproperty
    def children(self):
        pass

    #override if needed
    def to_string(self):
        return self.__class__.__name__

    def push_data(self, data):
        if not self.children():
            return
        if len(self.children()) == 0:
            return
        child_length = len(self.children())
        child_array = self.children()
        if child_length == 1:
            child_array[0].on_enter(data)
        else:
            for i in range(0, child_length):
                if i == child_length - 1:
                    self.children()[i].on_enter(data)
                else:
                    cp = copy.deepcopy(data)
                    self.children()[i].on_enter(cp)


class DataBus(object):
    def __init__(self):
        self.data = dict()
        self.datastring = "Created: " + str(datetime.now())
        self.modified = False

    def asrtval(self, name):
        a = dict.get(name, default=None)
        if not a:
            print('Warning! Invalid data type:' + name)
        return a


class ProcessingMode(object):
    def __init__(self, prcdelegate, *args, **kwargs):
        #parse kwargs
        toname = kwargs.get('toname', None)
        self.fromname = args
        self.prcdelegate = prcdelegate
        if toname:
            self.toname = toname
        else:
            print("WARNING! ambiguous return variable, setting to first one as default")
            self.toname = self.fromname[0]



