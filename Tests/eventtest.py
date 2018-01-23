import event as ev
import threshold as th


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

tre.on_enter(mockfile)