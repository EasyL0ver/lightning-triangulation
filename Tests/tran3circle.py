import datamodels as dm
from Modules import filtering as pre
from Modules import event as ev
from Modules import triang as tg
from Modules.threshold import ThresholdClusterBlock, ThresholdBlock, PowerBlock
from Modules import linelement as bsp



moqobs1 = dm.Observation()
moqobs1.certain = 100
moqobs1.sn_max_value = -20
moqobs1.ew_max_value = 20
moqobs1.file = dm.File()
moqobs1.file.location = dm.Location()
moqobs1.file.location.longitude = 20
moqobs1.file.location.latitude = 0



moqobs2 = dm.Observation()
moqobs2.certain = 100
moqobs2.sn_max_value = 500
moqobs2.ew_max_value = 500
moqobs2.file = dm.File()
moqobs2.file.location = dm.Location()
moqobs2.file.location.longitude = -20
moqobs2.file.location.latitude = 0


moqevent = dm.Event()
moqevent.obs1 = moqobs1
moqevent.obs1_id = 1
moqevent.obs2 = moqobs2
moqevent.obs2_id = 2

moqevlist = []
moqevlist.append(moqevent)
evbus = bsp.DataBus()

evbus.data['ev'] = moqevlist

angle = tg.AngleCalcBlock()
circle = tg.GreatCircleCalcBlock(vincenty_distance=500)

angle.children().append(circle)

angle.on_enter(evbus)







