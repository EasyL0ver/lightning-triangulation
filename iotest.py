import datetime as dt
import common
import datamodels
import dataprovider as dp
import ormprovider as orm
from Modules import filtering as pre
from Modules import event as ev
from Modules import triang as tg
from Modules.threshold import ThresholdClusterBlock, ThresholdBlock
from Modules import linelement as bsp


#setupdatastorage and converter
ormprov = orm.DataProvider();
dataprov = dp.DataProvider(ormprov.getActiveSession());
dataprov.datasources.append({'locname': "Hugo", 'filepath': r"D:\inzynierka\ImpulseDataAnalyzer"})
#dataprov.datasources.append({'locname': "Hylaty", 'filepath': r"D:\moje\inzynierka\testdata\Hylaty"})
#dataprov.datasources.append({'locname': "Patagonia", 'filepath': r"D:\moje\inzynierka\testdata\Patagonia"})
dataprov.loaddata()
dataprov.populate()

#bootstrap observation chain
th = ThresholdBlock(70, 1)
hpfilter = pre.HPFilter(0.05, 101, 'hamming')
prfilter = pre.RegionBasedBandStop(0.2, 101)
podglad = common.TestPlotBlock(1, 'pwr_th')
cluster = ThresholdClusterBlock(1600)

eventDec = ev.LocalMaximumEventBlock(10, 10)
eventEndpoint = ev.EntityToDbEndpoint(ormprov, 'obs')

hpfilter.children().append(prfilter)
prfilter.children().append(th)
th.children().append(podglad)
th.children().append(cluster)
cluster.children().append(eventDec)
eventDec.children().append(eventEndpoint)


#run -> szuakm wydarzen na zaladowanych danych
for data in dataprov.loadeddata:
    if data.eventscreated == 0:
       hpfilter.onenter(data.getbus())

eventEndpoint.flush()



#bootstrap event chain and group up events
observations = dataprov.currentdbsession.query(datamodels.Observation).all()
obsbus = bsp.DataBus()
obsbus.data['obs'] = observations


to = ev.TimeOffsetObservationConnectorBlock(dt.timedelta(seconds=0.1))
endpoint = ev.EntityToDbEndpoint(ormprov, 'ev')
to.children().append(endpoint)

to.onenter(obsbus)
endpoint.flush()

#load grouped up events and triangulate
events = dataprov.currentdbsession.query(datamodels.Event).all()
evbus = bsp.DataBus()
evbus.data['ev'] = events


angle = tg.AngleCalcBlock()
circle = tg.GreatCircleCalcBlock(vincentydist=500)
endpoint = ev.EntityToDbEndpoint(ormprov, 'ev')

angle.children().append(circle)
circle.children().append(endpoint)

angle.onenter(evbus)

endpoint.flush()
var =1





