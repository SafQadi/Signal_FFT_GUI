

import numpy as np


class MyFilter:
    """
    A filter class to apply first and second order low pass filters on time series.

    Author: Safwan Al-Qadhi
    Last modified: 22.07.2021

    Parameters:

        Cutoff-frequency (Hz)
        sampling ratio (Samples/sec.)

        output:
        filtered signal
    """


    def __init__(self, freq, sample):

        self._cutoff_freq = freq
        self._dt = sample

        #  dt = 2000.0 * 0.000001f //  omega = 2.0f * M_PI* filterFreq * refreshRate * 0.000001f
        self._omega = 2.0 * np.pi * self._cutoff_freq * self._dt
        self._sn = np.sin(self._omega)
        self._cs = np.cos(self._omega)
        self._alpha = self._sn / (2.0 * 0.7071)  # Q=2

        # b0 = 0, b1 = 0, b2 = 0, a0 = 0, a1 = 0, a2 = 0
        self._b0 = (1 - self._cs) * 0.5
        self._b1 = 1 - self._cs
        self._b2 = (1 - self._cs) * 0.5
        self._a0 = 1 + self._alpha
        self._a1 = -2 * self._cs
        self._a2 = 1 - self._alpha

        # normalize the coefficients
        self._filter_b0 = self._b0 / self._a0
        self._filter_b1 = self._b1 / self._a0
        self._filter_b2 = self._b2 / self._a0
        self._filter_a1 = self._a1 / self._a0
        self._filter_a2 = self._a2 / self._a0

        self._x1 = 0
        self._x2 = 0

        self._RC = 1 / (2 * np.pi * self._cutoff_freq)
        self._Gain = self._dt / (self._RC + self._dt)

        self.pt1_result = 0

    def biquad_filter(self, signal):
        result = self._filter_b0 * signal + self._x1
        self._x1 = self._filter_b1 * signal - self._filter_a1 * result + self._x2
        self._x2 = self._filter_b2 * signal - self._filter_a2 * result
        #result = result * 0.99
        return result

    def pt1_filter(self, signal):

        self.pt1_result = self.pt1_result + self._Gain * (signal - self.pt1_result)

        return self.pt1_result

