import datetime as dt
import common
import datamodels
import dataprovider as dp
import ormprovider as orm
from Modules import filtering as pre
from Modules import event as ev
from Modules import triang as tg
from Modules.threshold import ThresholdClusterBlock, ThresholdBlock, PowerBlock
from Modules import linelement as bsp


freshBaseSetting = True
copyRaw = False
plotBlocksOn = True

#setupdatastorage and converter
ormprov = orm.DataProvider(freshBaseSetting);
dataprov = dp.DataProvider(ormprov.getActiveSession());
dataprov.datasources.append({'locname': "Hugo", 'filepath': r"D:\inzynierka\inz\Hugo"})
dataprov.datasources.append({'locname': "Hylaty", 'filepath': r"D:\inzynierka\inz\Hylaty"})
dataprov.datasources.append({'locname': "Patagonia", 'filepath': r"D:\inzynierka\inz\Patagonia"})

dataprov.loaddata(copy_raw=copyRaw)
dataprov.populate()


#bootstrap observation chain
th = ThresholdBlock(35, 50, 'env')
pw = PowerBlock()
env = pre.HilbertEnvelopeBlock('pwr')
#aadecon = pre.AntiAliasingDeconvolveBlock(0.99, 11, 'hamming')
hpfilter = pre.HPFilter(0.05, 101, 'hamming')
prfilter = pre.RegionBasedBandStop(0.05, 101)
podglad = common.TestPlotBlock(1, plotBlocksOn, 'env', "pwr_th")
cluster = ThresholdClusterBlock(10)

eventDec = ev.LocalMaximumEventBlock(100, 200, 350)
eventEndpoint = ev.EntityToDbEndpoint(ormprov, 'obs')

#aadecon.children().append(hpfilter)
hpfilter.children().append(prfilter)
prfilter.children().append(pw)
th.children().append(podglad)
pw.children().append(env)
env.children().append(th)
th.children().append(cluster)
cluster.children().append(eventDec)
eventDec.children().append(eventEndpoint)

#run -> szuakm wydarzen na zaladowanych danych
for data in dataprov.loadeddata:
    if data.eventscreated == 0:
       hpfilter.onenter(data.getbus())

eventEndpoint.flush()



#bootstrap event chain and group up events
observations = dataprov.currentdbsession.query(datamodels.Observation)\
    .order_by(datamodels.Observation.certain.desc())

obsbus = bsp.DataBus()
obsbus.data['obs'] = observations


to = ev.TimeOffsetObservationConnectorBlock(dt.timedelta(seconds=0.5), 90)
endpoint = ev.EntityToDbEndpoint(ormprov, 'ev')
to.children().append(endpoint)

to.onenter(obsbus)
endpoint.flush()

#load grouped up events and triangulate
events = dataprov.currentdbsession.query(datamodels.Event).all()
evbus = bsp.DataBus()

testlist = []
testlist.append(events[2])
evbus.data['ev'] = testlist


angle = tg.AngleCalcBlock()
circle = tg.GreatCircleCalcBlock(vincentydist=500)
endpoint = ev.EntityToDbEndpoint(ormprov, 'ev')

angle.children().append(circle)
circle.children().append(endpoint)

angle.onenter(evbus)

endpoint.flush()



hpplot = pre.HPFilter(0.05, 101, 'hamming')
prplot = pre.BandStopFilter(0.1, 0.05, 101)
prplot = pre.RegionBasedBandStop(0.05, 101)
#common.mfreqz(prplot.filter)
podgladplot = common.TestPlotBlock(1, True, 'sn', "ew")

hpplot.children().append(podgladplot)
prplot.children().append(podgladplot)
common.printrange(dataprov, dt.datetime(year=2016, month=3, day=30, hour=21, minute=47, second=47, microsecond=500000), 2, podgladplot)

var =1


