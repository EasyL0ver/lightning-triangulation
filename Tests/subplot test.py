
import matplotlib.pyplot as plt
from Modules import linelement as bsp
import datetime as dt
import numpy as np
from matplotlib import gridspec


x = np.arange(0, 10, 0.2)
y = np.sin(x)

# plot it
fig = plt.figure(1)
gs = gridspec.GridSpec(4, 1, height_ratios=[0, 1, 1, 1])
ax0 = plt.subplot(gs[0])
ax0.plot(x, y)
ax1 = plt.subplot(gs[1])
ax1.plot(y, x)



plt.tight_layout()
plt.show()
#plt.savefig('grid_figure.pdf')