import dataprovider as dp
import ormprovider as orm
import datamodels as dm
import dataprovider as dp
import datetime as dt
import common



ormprov = orm.DataProvider();
dataprov = dp.DataProvider(ormprov.getActiveSession());
dataprov.datasources.append(r"D:\inzynierka\ImpulseDataAnalyzer")
dataprov.loaddata()
dataprov.populate()

# 2017-08-09 21:10:00.000854

startdate = dt.datetime(year=2017,day=9,hour=21,minute=9,month=8, second=30)
data = dataprov.getdata(startdate,400)
print("")





