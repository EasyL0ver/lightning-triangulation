from abc import ABCMeta, abstractmethod


class BaseSignalProcessor:
    __metaclass__ = ABCMeta

    @abstractmethod
    def getChildren(self):
        return self.children

    @abstractmethod
    def process(self, data):
        pass

    def pushDataToChildren(self,data):
        for i in range(0, len(self.getChildren)):
            self.getChildren[i].process(data)


