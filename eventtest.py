import filtering as pre
import threshold as th
import ormprovider as orm
import dataprovider as dp
import event as ev



class mockfile:
    def __init__(self):
        self.arrdata = None
        self.id = 100

    def getdataarr(self):
        return self.arrdata


mocktreshdata = [3, 1, 0, 1, 3, 1, 1, 0, 0, 0, 1, 3, 0, 1]

mockfile = mockfile()
mockfile.arrdata = [None] * 4
mockfile.arrdata[0] = mocktreshdata



tre = th.ThresholdBlock(0.5,1)
tclu = th.ThresholdClusterBlock()
event = ev.LocalMaximumEventBlock(1,1)


tre.children.append(tclu)
tclu.children.append(event)

tre.onenter(mockfile)