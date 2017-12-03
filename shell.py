import filtering as pre
import threshold as th
import ormprovider as orm
import dataprovider as dp
import event as ev
import datamodels
import datetime as dt
import triang as tg
import common


#static method returning possible locations
def locations(self):
    pass

#setupdatastorage and converter
ormprov = orm.DataProvider();
dataprov = dp.DataProvider(ormprov.getActiveSession());
dataprov.datasources.append(r"D:\moje\inzynierka\ImpulseDataAnalyzer")
dataprov.loaddata()
dataprov.populate()

#bootstrap observation chain
entry = th.ThresholdBlock(40, 1)
threshCluster = th.ThresholdClusterBlock(deadlen=400)

eventDec = ev.LocalMaximumEventBlock(10, 10)
eventEndpoint = ev.EntityToDbEndpoint(ormprov)

entry.children.append(threshCluster)
threshCluster.children.append(eventDec)
eventDec.children.append(eventEndpoint)


#run -> szuakm wydarzen na zaladowanych danych
for data in dataprov.loadeddata:
    if data.eventscreated == 0:
        entry.onenter(data)
eventEndpoint.flush()



#bootstrap event chain and group up events
observations = dataprov.currentdbsession.query(datamodels.Observation).all()

to = ev.TimeOffsetObservationConnectorBlock(dt.timedelta(seconds=1))
endpoint = ev.EntityToDbEndpoint(ormprov)
to.children.append(endpoint)

to.onenter(observations)
endpoint.flush()

#load grouped up events and triangulate
events = dataprov.currentdbsession.query(datamodels.Event).all()

angle = tg.AngleCalcBlock()
circle = tg.GreatCircleCalcBlock(vincentydist=500)
endpoint = ev.EntityToDbEndpoint(ormprov)

angle.children.append(circle)
circle.children.append(endpoint)

angle.onenter(events)

endpoint.flush()
var =1





