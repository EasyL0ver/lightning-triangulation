import filtering as pre
import threshold as th
import ormprovider as orm
import dataprovider as dp
import event as ev
import datamodels
import common

#setupdatastorage and converter
ormprov = orm.DataProvider();
dataprov = dp.DataProvider(ormprov.getActiveSession());
dataprov.datasources.append(r"D:\inzynierka\ImpulseDataAnalyzer")
dataprov.loaddata()
dataprov.populate()

#bootstrap
#filterTest = pre.BandStopFilter(taps=101, band=0.5, bandwidth=0.2)
threshTest = th.ThresholdBlock(40,1)
threshCluster = th.ThresholdClusterBlock()

#outputBlock = common.TestPlotBlock(3,plot=True)
#outputBlock2 = common.TestPlotBlock(2,plot=True)
#outputBlock3 = common.TestPlotBlock(1,plot = False)


eventDec = ev.LocalMaximumEventBlock(10,10)
eventEndpoint = ev.EventToDbEndpoint(ormprov)

threshTest.children.append(threshCluster)
threshCluster.children.append(eventDec)
eventDec.children.append(eventEndpoint)

#common.mfreqz(filterPre.filter)




#run
threshTest.onenter(dataprov.loadeddata[0])
eventEndpoint.flush()



chalko = ormprov.getActiveSession().query(datamodels.Event).all()
test = chalko[20]

#print event
file = common.binarytonp(test.file.dat1)
output = file[test.firstsample:test.firstsample+test.samplelen]

var = 1









