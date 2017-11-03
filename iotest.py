import InputConverter as io
import filtering as pre
import threshold as th
from pylab import *
import common
import time


testInstance = io.InputConverter(65536/2,19.54)
start = time.time()

conversionError = common.ConversionError()
data = testInstance.convert(r"D:\moje\inzynierka", "1.dat", conversionError)
end = time.time()
print("time elapsed " + str(end - start))

if(conversionError.conversionSucces):
    print("Conversion succesful")
if(conversionError.conversionSucces == False):
    print("Conversion failed: " + conversionError.conversionErrorLog)


#bootstrap
filterPre= pre.HPFilter(cutoff=0.7, taps=101, window='hamming')
filterTest = pre.BandStopFilter(taps=101, band=0.5, bandwitdh=0.2)
threshTest = th.ThresholdBlock(40,1)

outputBlock = common.TestPlotBlock(3,plot=True)
outputBlock2 = common.TestPlotBlock(2,plot=True)
outputBlock3 = common.TestPlotBlock(1,plot = False)

filterPre.getChildren().append(filterTest)
filterTest.getChildren().append(threshTest)
filterTest.getChildren().append(outputBlock2)
threshTest.getChildren().append(outputBlock)

#common.mfreqz(filterPre.filter)

#run
filterTest.process(data.data[0,])







