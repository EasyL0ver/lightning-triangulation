import copy

from Data import datamodels
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
deconv = pre.DeconvolutionBlock(r"D:\inzynierka\ImpulseDataAnalyzer\gf_ELA10v6_NEW.data", True)
file = dataprov.orm_provider.get_session().query(datamodels.File).all()
f = file[1]
data = f.load_data()['sn']


data = hpfilter.flt(data)
data2 = copy.deepcopy(data)
data2 = hpfilter.flt(data2)
#data2 = np.zeros(256335)
data2 = deconv.flt(data2)
data = hpfilter.flt(data)


deconv_res = np.zeros(len(data))
deconv_res[0:len(data)-10000] = data2
deconv = deconv_res

plt.figure(1)
span = np.arange(len(data)).astype(float) / float(887)
plt.xlabel("Time [s]")
plt.ylabel("Amplitude [pT]")
plt.plot(span, data)
plt.plot(span, deconv)

plt.show()