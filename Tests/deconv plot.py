import copy

import datamodels
import matplotlib.pyplot as plt
import numpy as np

import Data.dataprovider as dp
from Modules import filtering as pre

debug_plot_blocks_enabled = False
show_all_obs = False
show_all_events = True
show_single_events = False
show_all_files = True
show_all_files_fft = False

#setupdatastorage and converter
dataprov = dp.DataProvider(drop_db=False);
dataprov.populate()

hpfilter = pre.HPFilter(0.05, 101, 'hamming')
deconv = pre.DeconvolutionBlock(r"D:\inzynierka\ImpulseDataAnalyzer\gf_ELA10v6_NEW.data")
file = dataprov.orm_provider.get_session().query(datamodels.Observation).all()
f = file[1]
data = f.load_data()['sn']

data2 = copy.deepcopy(data)
data2 = hpfilter.flt(data2)
#data2 = deconv.flt(data2)
data = hpfilter.flt(data)

zeros = np.zeros(5000)

data2 = np.concatenate(zeros,data2,zeros)
plt.figure(1)
span = np.arange(len(data2)).astype(float) / file.fsample
plt.xlabel("Time [s]")
plt.ylabel("Amplitude [pT]")
plt.plot(span, data2)
plt.plot(span, data)


