import Modules.filtering as flt
import scipy.signal as signal
import numpy as np
import matplotlib.pyplot as plt
import copy


def flt(data, resampled_mask_h):
    data_transform = np.fft.fft(data)
    for i in range(0, len(data)):
        data_transform[i] = data_transform[i] / resampled_mask_h[i]
    output = np.fft.ifft(data_transform)
    norm_factor = max(data) / max(output)
    return np.real(output) * norm_factor

n = 100


input = np.zeros(n)
input[30:60] = signal.sawtooth(np.arange(30))

kernel = np.random.rand(20)
kernelf = np.fft.fft(kernel, n)
noised_input = signal.convolve(input, kernel, mode="same")
noised_input2 = signal.convolve(input, kernel, mode="same")


c = flt(copy.deepcopy(noised_input), kernelf)
c2, rm = signal.deconvolve(noised_input, kernelf)

plt.figure(1)
plt.plot(input)
plt.plot(noised_input)
plt.plot(c)
plt.show()


plt.figure(1)
plt.plot(input)
plt.plot(noised_input2)
plt.plot(c2)
plt.show()


