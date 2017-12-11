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


#setupdatastorage and converter
ormprov = orm.DataProvider();
dataprov = dp.DataProvider(ormprov.getActiveSession());
dataprov.datasources.append({'locname': "Hugo", 'filepath': r"D:\inzynierka\inz\Hugo"})
dataprov.datasources.append({'locname': "Hylaty", 'filepath': r"D:\inzynierka\inz\Hylaty"})
dataprov.datasources.append({'locname': "Patagonia", 'filepath': r"D:\inzynierka\inz\Patagonia"})


loc = dataprov.currentdbsession.query(datamodels.Location).all()
#moq = common.creatmockdata(loc[0],9600)
#moq1 =common.creatmockdata(loc[1],10000)
#ormprov.getActiveSession().add(moq)
#ormprov.getActiveSession().add(moq1)
#ormprov.getActiveSession().commit()

dataprov.loaddata()
dataprov.populate()


#bootstrap observation chain
th = ThresholdBlock(40, 50, 'env')
pw = PowerBlock()
env = pre.HilbertEnvelopeBlock('pwr')
#aadecon = pre.AntiAliasingDeconvolveBlock(0.99, 11, 'hamming')
hpfilter = pre.HPFilter(0.05, 101, 'hamming')
prfilter = pre.RegionBasedBandStop(0.1, 101)
#podglad = common.TestPlotBlock(1, 'env', 'pwr_th')
cluster = ThresholdClusterBlock(10)

eventDec = ev.LocalMaximumEventBlock(100, 8000, 150)
eventEndpoint = ev.EntityToDbEndpoint(ormprov, 'obs')

#aadecon.children().append(hpfilter)
hpfilter.children().append(prfilter)
prfilter.children().append(pw)
#th.children().append(podglad)
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


to = ev.TimeOffsetObservationConnectorBlock(dt.timedelta(seconds=0.2), 70)
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





