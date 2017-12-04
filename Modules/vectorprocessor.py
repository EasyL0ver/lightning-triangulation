from abc import ABCMeta, abstractmethod, abstractproperty
## TODO ZROB TUTAJ TYPECHECK i TO STRING


class BaseProcessor:
    __metaclass__ = ABCMeta
    def onenter(self, file):
        data = self.process(file)
        self.pushdat(data)

    @abstractmethod
    def process(self, file):
        pass

    def pushdat(self, data):
        if self.children:
            for i in range(0, len(self.children)):
                self.children[i].onenter(data)


class VectorProcessor(BaseProcessor):
    __metaclass__ = ABCMeta

    #override
    def onenter(self, file):
        datarr = file.getdataarr()
        for i in range(0, len(datarr)):
            dat = datarr[i]
            if dat is not None:
                datarr[i] = self.process(datarr[i])
                file.cachedatamodified = True
        self.pushdat(file)

