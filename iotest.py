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
from Modules import plot


drop_db = False
copy_raw = False
plot_enabled = False

#setupdatastorage and converter
dataprov = dp.DataProvider(drop_db);
dataprov.add_source("Hugo", r"D:\moje\inzynierka\inz\Hugo")
dataprov.add_source("Hylaty", r"D:\moje\inzynierka\inz\Hylaty")
dataprov.add_source("Patagonia", r"D:\moje\inzynierka\inz\Patagonia")

dataprov.load_data(copy_raw=copy_raw)
dataprov.populate()


#bootstrap observation chain
th = ThresholdBlock(35, 50, 'env')
pw = PowerBlock()
env = pre.HilbertEnvelopeBlock('pwr')
hpfilter = pre.HPFilter(0.05, 101, 'hamming')
prfilter = pre.RegionBasedBandStop(0.05, 101)
cluster = ThresholdClusterBlock(10)

eventDec = ev.LocalMaximumEventBlock(200, 200, 350)
eventEndpoint = ev.EntityToDbEndpoint(dataprov, 'obs')

hpfilter.children().append(prfilter)
prfilter.children().append(pw)
pw.children().append(env)
env.children().append(th)
th.children().append(cluster)
cluster.children().append(eventDec)
eventDec.children().append(eventEndpoint)

#run -> szukam wydarzen na zaladowanych danych
for data in dataprov.loaded_data:
    if data.eventscreated == 0:
       hpfilter.on_enter(data.load_data())

eventEndpoint.flush()

#bootstrap event chain and group up events
obsbus = bsp.DataBus()
observations = dataprov.orm_provider.get_session().query(datamodels.Observation).order_by(datamodels.Observation.certain.desc()).all()

hppl = pre.HPFilter(0.05, 101, 'hamming')
oplot = plot.ObservationPlotBlock()

hppl.children().append(oplot)
for obs in observations:
    hppl.on_enter(obs.get_data())

to = ev.TimeOffsetObservationConnectorBlock(dt.timedelta(seconds=0.5), 90)
endpoint = ev.EntityToDbEndpoint(dataprov, 'ev')
to.children().append(endpoint)

to.on_enter(obsbus)
endpoint.flush()

#load grouped up events and triangulate
events = dataprov.orm_provider.get_session().query(datamodels.Event).all()
evbus = bsp.DataBus()

testlist = []
testlist.append(events[2])
evbus.data['ev'] = testlist


angle = tg.AngleCalcBlock()
circle = tg.GreatCircleCalcBlock(500)
endpoint = ev.EntityToDbEndpoint(dataprov, 'ev')

angle.children().append(circle)
circle.children().append(endpoint)

angle.on_enter(evbus)

endpoint.flush()



hpplot = pre.HPFilter(0.05, 101, 'hamming')
prplot = pre.BandStopFilter(0.1, 0.05, 101)
prplot = pre.RegionBasedBandStop(0.01, 101)
#common.mfreqz(prplot.filter)
podgladplot = common.FftPlotBlock(1, True, 'sn')

hpplot.children().append(prplot)
prplot.children().append(podgladplot)

common.printrange(dataprov, dt.datetime(year=2016, month=3, day=30, hour=21, minute=47, second=47, microsecond=500000), 2, hpplot)

var =1


