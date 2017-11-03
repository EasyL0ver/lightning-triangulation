class UserMarkingViewSub:
    def __init__(self, defaultShownWidth, startingMarkerWidth,  parent, dataContent, targetName, savePath):
        self.startingShownIndex = 0
        self.defaultShownWidth = defaultShownWidth
        self.startingMarkerWidth = startingMarkerWidth
        self.maximumContentWidth = len(dataContent)
        self.currentMarkers = []
        self.dataContent = dataContent
        self.parent = parent

    def getShownRange(self):
        return range(self.startingShownIndex, self.startingShownIndex + self.defaultShownWidth)

    def getCurrentMarker(self):
        for i in range(0, len(self.currentMarkers)):
            if self.currentMarkers[i].isActive:
                return self.currentMarkers[i]
        return

    def createMarker(self, mousePosition):
        for i in range(0, len(self.currentMarkers)):
            self.currentMarkers[i].isActive = False
        marker = FunctionMarker(mousePosition, self.startingMarkerWidth)
        if (mousePosition + self.startingMarkerWidth) > self.maximumContentWidth :
            marker = FunctionMarker(mousePosition, self.maximumContentWidth)
        self.currentMarkers.append(marker)

    def deleteCurrentMarker(self):
        self.currentMarkers.remove(self.getCurrentMarker())

    def finishedit(self):
        #tutaj wpisz dane do stosowoengo txtka w zaleznosci od name
        self.parent.finishcurrent()

class FunctionMarker:
    def __init__(self, firstposition, secondposition):
        self.isActive = True
        self.firstPosition = firstposition
        self.secondPosition = secondposition
        self.markerType = "default"
        self.comment = ""



