import baseprocessor as bsp
import math


class AngleCalcBlock(bsp.FileProcessor):
    def __init__(self):
        self.children = []

    def process(self, inevents):
        #assert events data
        for event in inevents:
            if event.obs1_id:
                event.ob1_angle = self.calcangle(event.obs1)
            if event.obs2_id:
                event.ob2_angle = self.calcangle(event.obs2)
            if event.obs3_id:
                event.ob3_angle = self.calcangle(event.obs3)
        return inevents

    def calcangle(self, inputobs):
        return math.atan(inputobs.sn_max_value/inputobs.ew_max_value)






