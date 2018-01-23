import datetime as dt
import templates
from Data import dataprovider as dp
from Modules import event as ev
from Modules import linelement as bsp
from Modules import triang as tg
from Modules import filtering as flt
from Data import datamodels
from Modules.threshold import ThresholdClusterBlock, ThresholdBlock, PowerBlock

drop_db = True
copy_raw = False

read_deconvolution_enabled = False

#setupdatastorage and converter
dataprov = dp.DataProvider(drop_db);
dataprov.add_source("Hugo", r"D:\inzynierka\inz\Hugo", filter='2016')
dataprov.add_source("Hylaty", r"D:\inzynierka\inz\Hylaty", filter='033')
dataprov.add_source("Patagonia", r"D:\inzynierka\inz\Patagonia")

dataprov.load_data(copy_raw=copy_raw)
dataprov.populate()


#bootstrap observation chain
pre_processing_block = templates.pre_processing_template()
pw = PowerBlock()
th = ThresholdBlock(35, 50, 'pwr')
cluster = ThresholdClusterBlock(10)
deconv = flt.DeconvolutionBlock(r"D:\inzynierka\ImpulseDataAnalyzer\gf_ELA10v6_NEW.data", read_deconvolution_enabled)

eventDec = ev.LocalMaximumEventBlock(200, 200, 350)
eventEndpoint = ev.EntityToDbEndpoint(dataprov, 'obs')

pre_processing_block.children().append(pw)
pw.children().append(th)
th.children().append(cluster)
cluster.children().append(eventDec)
eventDec.children().append(eventEndpoint)

#run -> szukam wydarzen na zaladowanych danych
for data in dataprov.loaded_data:
    if data.eventscreated == 0:
       pre_processing_block.on_enter(data.load_data())

eventEndpoint.flush()

#bootstrap event chain and group up events
obsbus = bsp.DataBus()
observations = dataprov.orm_provider.get_session().query(datamodels.Observation).order_by(
    datamodels.Observation.certain.desc()).all()
obsbus['obs'] = observations
to = ev.TimeOffsetObservationConnectorBlock(dt.timedelta(seconds=0.5), 90)
endpoint = ev.EntityToDbEndpoint(dataprov, 'ev')
to.children().append(endpoint)

to.on_enter(obsbus)
endpoint.flush()

#load grouped up events and triangulate
events = dataprov.orm_provider.get_session().query(datamodels.Event).all()
evbus = bsp.DataBus()
evbus.data['ev'] = events

angle = tg.AngleCalcBlock()
circle = tg.GreatCircleCalcBlock(500)
endpoint = ev.EntityToDbEndpoint(dataprov, 'ev')

angle.children().append(circle)
circle.children().append(endpoint)

angle.on_enter(evbus)
endpoint.flush()




