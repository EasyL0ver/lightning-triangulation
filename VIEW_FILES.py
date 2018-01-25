import settings
import templates
from Data import dataprovider as dp
from dateutil import parser
from Data import datamodels
from Modules import filtering as pre
from Modules import plot
from Modules import threshold as th
from Modules import linelement as bsp
import datetime as dt
from Data import common

deconvolution_mask_path = settings.deconvolution_mask_path()
dataprov = dp.DataProvider(drop_db=False)
dataprov.populate()

filelen = dt.timedelta(minutes=5)
filtername = None
template = bsp.NullBlock()
plotblock = plot.BaseAsyncPlotBlock(1, True , 'sn', 'ew')
amount = 1

print("Print data from all stations ?")
allstats = str(raw_input('y/n ?:'))
if allstats == 'y':
    print('Plotting data from all stations chosen')
    filtername = None
else:
    filtername = str(raw_input('Specify station name'))

print("Use filtering ?")
allstats = str(raw_input('y/n ?:'))
if allstats == 'y':
    print('Pre-Processing template will be used, modify in templates.py')
    template = templates.pre_processing_template()

a = str(raw_input('Specify starting date-time '))
startdatetime = parser.parse(a)
print("Parsed date time is: " + str(startdatetime))

a = str(raw_input('Specify ending date-time '))
enddatetime = parser.parse(a)
print("Parsed date time is: " + str(enddatetime))
enddatetime = enddatetime - filelen

amount = int(raw_input('How many files to print ?'))
print("Select plotting mode \n 1. SN/EW timeseries \n 2. FFT")
allstats = str(raw_input("Select number:"))
if allstats == '1':
    plotblock = plot.FilePlotBlock()
if allstats == '2':
    plotblock = plot.FilePlotBlock(mode='fft')

a = str(raw_input('Press any key to start plotting'))

querytimestart = startdatetime.date() - dt.timedelta(days=1)
querytimeend = enddatetime.date() + dt.timedelta(days=1)
if not filtername:
    files = dataprov.orm_provider.get_session().query(datamodels.File).filter((datamodels.File.date > querytimestart) & (datamodels.File.date < querytimeend)).all()
else:
    files = dataprov.orm_provider.get_session().query(datamodels.File).join(datamodels.Location).filter(
        (datamodels.File.date > querytimestart)
        & (datamodels.Location.name == filtername)).all()

if len(files) == 0:
    print("Nothing to plot, aborting")
inpt = []
for file in files:
    datetime = common.cmbdt(file.date,file.time)
    if enddatetime > datetime > startdatetime:
        inpt.append(file)

inpt = sorted(inpt, key=lambda x: common.cmbdt(x.date, x.time), reverse=True)

template.children().append(plotblock)

for file in inpt:
    if amount > 0:
        template.on_enter(file.load_data())
        amount -= 1