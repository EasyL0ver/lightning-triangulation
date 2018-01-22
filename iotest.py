import datetime as dt
import datamodels
import dataprovider as dp
from Modules import filtering as pre
from Modules import event as ev
from Modules import triang as tg
from Modules.threshold import ThresholdClusterBlock, ThresholdBlock, PowerBlock
from Modules import linelement as bsp
from Modules import plot


drop_db = True
copy_raw = False

debug_plot_blocks_enabled = False
show_all_obs = False
show_all_events = False
show_single_events = True
show_all_files = False

#setupdatastorage and converter
dataprov = dp.DataProvider(drop_db);
dataprov.add_source("Hugo", r"D:\inzynierka\inz\Hugo")
dataprov.add_source("Hylaty", r"D:\inzynierka\inz\Hylaty")
dataprov.add_source("Patagonia", r"D:\inzynierka\inz\Patagonia")

dataprov.load_data(copy_raw=copy_raw)
dataprov.populate()


#create pre-processing template
hpfilter = pre.HPFilter(0.05, 11, 'hamming')
prfilter = pre.RegionBasedBandStop(0.05, 11)
hpfilter.children().append(prfilter)
pre_processing_template = bsp.ProcessorTemplateBlock(hpfilter)


#bootstrap observation chain
flttemplate = pre_processing_template.get_instance()
th = ThresholdBlock(35, 50, 'env')
pw = PowerBlock()
env = pre.HilbertEnvelopeBlock('pwr')
cluster = ThresholdClusterBlock(10)
podglad = plot.BaseAsyncPlotBlock(1, True, 'sn')


eventDec = ev.LocalMaximumEventBlock(200, 200, 350)
eventEndpoint = ev.EntityToDbEndpoint(dataprov, 'obs')

flttemplate.children().append(pw)
pw.children().append(env)
env.children().append(th)
th.children().append(cluster)
cluster.children().append(eventDec)
eventDec.children().append(eventEndpoint)

#run -> szukam wydarzen na zaladowanych danych
for data in dataprov.loaded_data:
    if data.eventscreated == 0:
       flttemplate.on_enter(data.load_data())

eventEndpoint.flush()

#bootstrap event chain and group up events
obsbus = bsp.DataBus()
observations = dataprov.orm_provider.get_session().query(datamodels.Observation).order_by(datamodels.Observation.certain.desc()).all()
obsbus['obs'] = observations

#show all observations example
if show_all_obs:
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
evbus.data['ev'] = events


angle = tg.AngleCalcBlock()
circle = tg.GreatCircleCalcBlock(500)
endpoint = ev.EntityToDbEndpoint(dataprov, 'ev')

angle.children().append(circle)
circle.children().append(endpoint)

angle.on_enter(evbus)
endpoint.flush()


#events plot example
if show_all_events:
    pass

if show_single_events:
    events = dataprov.orm_provider.get_session().query(datamodels.Event).all()
    evplot = plot.EventPlotBlock(dsp_template_instance=pre_processing_template.get_instance())
    for event in events:
        evplot.on_enter(event.get_data())

#files plot example
if show_all_files:
    files = dataprov.orm_provider.get_session().query(datamodels.File).all()
    plot_instance = pre_processing_template.get_instance()
    fiplot = plot.FilePlotBlock()

    plot_instance.children().append(fiplot)
    for file in files:
        plot_instance.on_enter(file.load_data())



var =1


