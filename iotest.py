import filtering as pre
import threshold as th
import ormprovider as orm
import dataprovider as dp
import event as ev
import datamodels
import datetime as dt
import common

#setupdatastorage and converter
ormprov = orm.DataProvider();
dataprov = dp.DataProvider(ormprov.getActiveSession());
dataprov.datasources.append(r"D:\inzynierka\ImpulseDataAnalyzer")
dataprov.loaddata()
dataprov.populate()

#bootstrap observation chain
entry= th.ThresholdBlock(40,1)
threshCluster = th.ThresholdClusterBlock()

eventDec = ev.LocalMaximumEventBlock(10,10)
eventEndpoint = ev.EntityToDbEndpoint(ormprov)

entry.children.append(threshCluster)
threshCluster.children.append(eventDec)
eventDec.children.append(eventEndpoint)


#run -> szuakm wydarzen na zaladowanych danych
for data in dataprov.loadeddata:
    if data.eventscreated == 0:
        entry.onenter(data)
eventEndpoint.flush()



#bootstrap event chain
unassignedobservations = dataprov.currentdbsession.query(datamodels.Observation).filter(datamodels.Observation.is_assigned == 0).all()


to = ev.TimeOffsetObservationConnectorBlock(dt.timedelta(seconds=1))
endpoint = ev.EntityToDbEndpoint(ormprov)
to.children.append(endpoint)

to.onenter(unassignedobservations)
endpoint.flush()

var = 1








