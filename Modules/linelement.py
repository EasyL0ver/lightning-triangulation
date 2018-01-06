from abc import ABCMeta, abstractmethod, abstractproperty
from datetime import datetime
import copy


class BaseProcessor:
    __metaclass__ = ABCMeta
    def onenter(self, dbus):
        print("Current module " + self.tostring())
        processing_modes = self.prcmodes()
        for mode in processing_modes:
            tup = []
            for argument in mode.fromname:
                tup.append(dbus.data[argument])
            dbus.data[mode.toname] = mode.prcdelegate(*tup)
        dbus.modified = True
        dbus.datastring += " "
        dbus.datastring += self.tostring()
        self.pushdat(dbus)

    @abstractproperty
    def prcmodes(self):
        pass

    @abstractproperty
    def children(self):
        pass

    #override if needed
    def tostring(self):
        return self.__class__.__name__

    def pushdat(self, data):
        if not self.children():
            return
        if len(self.children()) == 0:
            return
        chldlen = len(self.children())
        chldarr = self.children()
        if chldlen == 1:
            chldarr[0].onenter(data)
        else:
            for i in range(0, chldlen):
                if i == chldlen - 1:
                    self.children()[i].onenter(data)
                else:
                    cp = copy.deepcopy(data)
                    self.children()[i].onenter(cp)


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



