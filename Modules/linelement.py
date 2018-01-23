from abc import ABCMeta, abstractmethod, abstractproperty
from datetime import datetime
import copy
import time


class BaseProcessor:
    __metaclass__ = ABCMeta

    def on_enter(self, dbus):
        print("Current module " + self.to_string() + "with input data " + str(dbus))
        start = time.time()
        processing_modes = self.processing_modes()
        for mode in processing_modes:
            tup = []
            for argument in mode.fromname:
                tup.append(dbus.data[argument])
            dbus.data[mode.toname] = mode.prcdelegate(*tup)
        dbus.modified = True
        dbus.datastring += " "
        dbus.datastring += self.to_string()
        end = time.time()
        print(str(processing_modes) + " finished. Time elapsed: " + str(end - start))
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


class ProcessorTemplateBlock(BaseProcessor):
    def on_enter(self, dbus):
        if self.is_instance:
            self.entry_point.on_enter(dbus)
        else:
            raise Exception("ERROR! Template used as processing block, use get_instance instead")

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def get_instance(self):
        #scaffold new template
        instance = ProcessorTemplateBlock(copy.deepcopy(self.entry_point))
        instance.is_instance = True
        external_nodes = []
        self.leaf_search(external_nodes, instance.entry_point)
        for external_node in external_nodes:
            external_node.children().append(InnerDataOutput(instance))
        return instance

    def leaf_search(self, collection, node):
        if not node.children() or len(node.children()) == 0:
            collection.append(node)
        else:
            for child in node.children():
                self.leaf_search(collection, child)

    def __init__(self, entry_point):
        self.is_instance = False
        self.entry_point = entry_point
        self.inner_data_block = None
        self._children = []
        self._prcmodes = []


class MemoryBlock(BaseProcessor):
    def on_enter(self, dbus):
        if not self.cachedData:
            self.cachedData = dbus

    def children(self):
        return self._children

    def processing_modes(self):
        return self._prcmodes

    def clear(self):
        self.cachedData = None

    def __init__(self):
        self.cachedData = None
        self._children = []
        self._prcmodes = []


class InnerDataOutput(BaseProcessor):
    def on_enter(self, dbus):
        for child in self._children:
            child.push_data(dbus)

    def children(self):
        return self._children

    def processing_modes(self):
        return None

    def __init__(self, template):
        self._children = []
        self._children.append(template)


class DataBus(object):
    def __init__(self):
        self.data = dict()
        self.datastring = "Created: " + str(datetime.now())
        self.modified = False

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __str__(self):
        return str(self.data.keys())

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

    def __repr__(self):
        return self.toname + " = " + self.prcdelegate.__name__ + " " + str(self.fromname)



