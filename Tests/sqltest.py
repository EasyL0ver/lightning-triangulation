from Data import ormprovider as orm, dataprovider as dp, common

ormprov = orm.DBProvider();
dataprov = dp.DataProvider(ormprov.get_session());
dataprov.sources.append(r"D:\inzynierka\ImpulseDataAnalyzer")
dataprov.load_data()
dataprov.load_data()
dataprov.load_data()
dataprov.populate()



loadtest = dataprov.loaded_data[0]

data = common.binarytonp(loadtest.dat1)
var = 1

