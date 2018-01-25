import settings
import templates
from Data import dataprovider as dp
from dateutil import parser
from Data import datamodels
from Modules import plot
from Modules import linelement as bsp
import datetime as dt
from Data import common

deconvolution_mask_path = settings.deconvolution_mask_path()
dataprov = dp.DataProvider(drop_db=False)
dataprov.populate()
filelen = dt.timedelta(seconds=30)
default_end_datetime = dt.timedelta(days=1)
singlemode = False
micert = 30


filtername = None
template = bsp.NullBlock()
minsub = 3


while True:
    print("Select plotting mode \n 1. single events \n 2. grouped events")
    allstats = str(raw_input("Select number:"))
    if allstats == '1':
        plotblock = plot.ObservationPlotBlock()
        singlemode = True
        print("Single event mode chosen")
        break
    elif allstats == '2':
        print("Grouped event mode chosen")
        break
    else:
        print("Bad input, try again")


if singlemode:
    while True:
        print("Print data from all stations ?")
        allstats = str(raw_input('y/n ?:'))
        if allstats == 'y':
            print('Plotting data from all stations chosen')
            filtername = None
            break
        elif allstats == 'n':
            filtername = str(raw_input('Specify station name'))
            break
        else:
            print("Bad input, try again")

    while True:
        try:
            micert = float(raw_input('Specify minimum amplitude to show :'))
            break
        except ValueError:
            print("Bad input, try again")


if not singlemode:
    while True:
        try:
            minsub = int(raw_input('Minimum sub observations available? (currently max = 3)'))
            break
        except ValueError:
            print("Bad input, try again")


while True:
    try:
        a = str(raw_input('Specify starting date-time '))
        startdatetime = parser.parse(a)
        print("Parsed date time is: " + str(startdatetime))
        break
    except ValueError:
        print("Bad input, try again")


enddatetime = startdatetime + default_end_datetime
enddatetime = enddatetime - filelen

while True:
    print("Use filtering ?")
    allstats = str(raw_input('y/n ?:'))
    if allstats == 'y':
        print('Pre-Processing template will be used, modify in templates.py')
        template = templates.pre_processing_template()
        break
    if allstats == 'n':
        break

#raw_input('press enter to start plotting')

querytimestart = startdatetime.date() - dt.timedelta(days=1)
querytimeend = enddatetime.date() + dt.timedelta(days=1)
if singlemode:
    if not filtername:
        obs = dataprov.orm_provider.get_session().query(datamodels.Observation)\
            .join(datamodels.File).filter((datamodels.File.date > querytimestart) &
                                          (datamodels.File.date < querytimeend) &
                                          ((datamodels.Observation.sn_max_value > micert) |
                                           (datamodels.Observation.sn_max_value < -micert)|
                                           (datamodels.Observation.ew_max_value > micert)|
                                           (datamodels.Observation.ew_max_value < -micert))).all()
    else:
        obs = dataprov.orm_provider.get_session().query(datamodels.Observation).join(datamodels.Location).filter(
            (datamodels.File.date > querytimestart)
            & (datamodels.Location.name == filtername) & ((datamodels.Observation.sn_max_value > micert) |
                                           (datamodels.Observation.sn_max_value < -micert)|
                                           (datamodels.Observation.ew_max_value > micert)|
                                           (datamodels.Observation.ew_max_value < -micert))).all()

    if len(obs) == 0:
        print("Nothing to plot, aborting")
    inpt = []
    for ob in obs:
        datetime = common.cmbdt(ob.file.date, ob.file.time)
        if enddatetime > datetime > startdatetime:
            inpt.append(ob)

    inpt = sorted(inpt, key=lambda x: common.cmbdt(x.file.date, x.file.time))

    template.children().append(plotblock)

    for obs in inpt:
        template.on_enter(obs.get_data())

else:
    events = dataprov.orm_provider.get_session().query(datamodels.Event).filter((datamodels.Event.index_date > querytimestart) & (datamodels.Event.index_date < querytimeend)).all()
    if len(events) == 0:
        print("Nothing to plot, aborting")
    inpt = []
    for ev in events:
        datetime = common.cmbdt(ev.index_date, ev.index_time)
        if enddatetime > datetime > startdatetime:
            if (minsub == 3 and ev.obs3 is not None) or (minsub == 2 and ev.obs2 is not None) or minsub == 1:
                inpt.append(ev)

    inpt = sorted(inpt, key=lambda x: common.cmbdt(x.index_date, x.index_time))
    evplot = plot.EventPlotBlock(dsp_template_instance=template)
    for event in inpt:
        evplot.on_enter(event.get_data())


