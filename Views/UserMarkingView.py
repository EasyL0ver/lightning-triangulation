class UserMarkingView:
    def __init__(self):
        self.directoriesList = []
        self.saveDirectory
        self.defaultShownWidth = 10000
        self.directoriesCounter = 0
        self.currentSubShown

    def activatesubview(self, subview):
        self.currentSubShown = subview

    def finishcurrent(self):
        self.directoriesCounter += 1;
        if self.directoriesCounter < len(self.directoriesList):
            self.activateSbView(self.directoriesList[self.directoriesCounter])

    def Initialize(self):
        self.activateSbView(self.directoriesList[0])










