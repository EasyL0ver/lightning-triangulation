#-*- coding: utf-8 -*-
import scipy.signal as signal

import matplotlib.pyplot as plt
import numpy as np
import random


input = np.zeros(300)
input[100:200] = 1
noise = np.random.rand(20)

changed = signal.convolve(input, noise, mode="same")
deconvolved, remainder = signal.deconvolve(changed, noise)


plt.figure(1)
plt.subplot(221)
plt.ylabel(u"Amplituda")
plt.xlabel(u"Numer próbki")
plt.title(u"Sygnał wejściowy")
plt.plot(input)
plt.subplot(222)
plt.ylabel(u"Amplituda")
plt.xlabel(u"Numer próbki")
plt.title(u"Funkcja h niechcianego splotu")
plt.plot(noise)
plt.subplot(223)
plt.ylabel(u"Amplituda")
plt.xlabel(u"Numer próbki")
plt.title(u"Sygnał wejściowy spleciony")
plt.plot(changed)
plt.subplot(224)
plt.ylabel(u"Amplituda")
plt.xlabel(u"Numer próbki")
plt.title(u"Sygnał po dekonwolucji")
plt.plot(deconvolved)

plt.tight_layout()
plt.show()