import ormprovider as orm
import datamodels as dm
import dataprovider as dp
import common


ormprov = orm.DataProvider();
dataprov = dp.DataProvider(ormprov.getActiveSession());
dataprov.datasources.append(r"D:\inzynierka\ImpulseDataAnalyzer")
dataprov.loaddata()
dataprov.loaddata()
dataprov.loaddata()
dataprov.populate()



loadtest = dataprov.loadeddata[0]

data = common.binarytonp(loadtest.dat1)
var = 1

