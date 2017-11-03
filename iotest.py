import InputConverter as io
import preprocessing as pre
from pylab import *
import common
import time


testInstance = io.InputConverter(65536/2,19.54)
start = time.time()

conversionError = common.ConversionError()
data = testInstance.convert(r"D:\moje\inzynierka", "1", conversionError)
end = time.time()
print("time elapsed " + str(end - start))

if(conversionError.conversionSucces):
    print("Conversion succesful")
if(conversionError.conversionSucces == False):
    print("Conversion failed: " + conversionError.conversionErrorLog)


#filtering test
filterPre= pre.PreProcessFilter(cutoff=0.3, taps=101, window= 'hamming')
start = time.time()
filteredData = filterPre.process(data.data[0,])
end = time.time()

print("filtering finished after  " + str(end - start))

figure(1)
common.mfreqz(filterPre.filter)
show()

figure(2)
plot(data.data[0,])
plot(filteredData)
show()




