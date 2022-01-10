from scipy.signal import butter, lfilter, freqz, filtfilt
import numpy as np
# from reo import data, t_counts
from matplotlib import pyplot as plt

def butter_bandpass(lowcut, highcut, fs, order = 2):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=2):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    output = lfilter(b, a, data)
    return output

# проверка  

# for order in [9]: 
#     fs = 32.125
#     b, a = butter_bandpass(0.000000005, 1, 32.125)
#     w, h = freqz(b, a, worN=2000)
#     plt.plot((fs * 0.5 / np.pi) * w, abs(h))
#     # plt.scatter(lowcut, 1)
#     # plt.scatter(highcut, 1)
# plt.show()


# output = butter_bandpass_filter(data, 0.05, 1, 32.125)
# # output2 = butterworth_high(data, 32.125, 0.3)
# # out = data - output - output2
# # out = out[7500:15000]
# # output = output[7500:15000]
# # t_counts = t_counts[7500:15000]
# # data = data[7500:15000]


# plt.figure()
# # plt.plot(t_counts, output, label='filtered')
# # plt.plot(t_counts[7500:15000], data[7500:15000], label = 'data')
# plt.plot(t_counts[7500:15000], output[7500:15000], label='filtered2')
# plt.legend()
# plt.show()