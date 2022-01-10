from BinFileUtils import defaultInfo, string2type, readHeader, readBinFile
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.patches as patches
from hdfdata import hdf_read

def spo2_desat(foldpath, curFile):
    Fs_reo, Fs_spo2, reo_ref, spo2_ref, ibeg, iend = hdf_read(foldpath, curFile)
    filepath = foldpath + '\\' + curFile + '.hdr'
    info, data = readBinFile(filepath)

    #spo2
    Fs = int(info['Fs'])
    k = Fs / 2 #2 герца - частота, к которой хотим привести
    data = np.array(data['SPOSoft']) / 10

    ibeg = int(ibeg / (Fs_spo2 / 2)) #приводим отсчеты начала и конца сна из .hdf файла к частоте 2 Гц
    iend = int(iend / (Fs_spo2 / 2))
    t_counts = np.arange(ibeg, iend)
    ibeg_data = int(info['iBeg'])
    iend_data = int(info['iEnd'])
    ibeg_diff = int(ibeg - ibeg_data / k)
    iend_diff = int(iend_data / k - iend)

    data = data[::int(k)]
    data = data[ibeg_diff : iend - ibeg + ibeg_diff]

    #создаём таблицу значений по секундам для удобства работы с циклом
    dict = {'data' : data,
            'n' : t_counts,
    }
    spo2 = pd.DataFrame(dict)
    # убираем отрицательные значения
    spo2.loc[spo2['data'] < 0, 'data'] = np.nan

    #таблица для результатов
    result = pd.DataFrame([[0] * 7], columns = ['ibeg_time', 'min_time', 'iend_time', 'a', 'b', 'c', 'T'])

    #цикл для обнаружения десатураций
    i = 1 
    z = 1
    while i < int(len(spo2)) + 1:
        q = 0
        if i + 2 > int(len(spo2) - 1):
            break
        if spo2['data'][i] <= spo2['data'][i + 2] or spo2['data'][i] - spo2['data'][i + 2] <= 0.1:
            i += 1
            continue
        elif 0.1 < spo2['data'][i] - spo2['data'][i + 2] < 4:
            a = spo2['data'][i]
            atime = spo2['n'][i]
            j = i
            if j + 4 > len(spo2) - 2:
                break
            while (spo2['data'][j] >= spo2['data'][j + 2] or spo2['data'][j] >= spo2['data'][j + 4]) and spo2['data'][j] - spo2['data'][j + 2] < 4: 
                j += 1
                if j + 4 > len(spo2) - 2:
                    break
            b = spo2['data'][j]
            btime = spo2['n'][j]
            if a - b >= 2:
                k = j + 1
                if k > int(len(spo2)) - 1:
                    break
                c = spo2['data'][k]
                ctime = spo2['n'][k]
                while a - c > 1 or c - b < 3:
                    if a - c <= 1 or c - b >= 3 or k > int(len(spo2) - 1):
                        break
                    k += 1
                    c = spo2['data'][k]
                    ctime = spo2['n'][k]
                    if k - i > 120:
                        q = 1
                        break
                if q == 1:
                    i = j
                    continue
                elif 20 <= ctime - atime <= 120:
                    result.loc[z, 'ibeg_time'] = atime
                    result.loc[z, 'min_time'] = btime
                    result.loc[z, 'iend_time'] = ctime
                    result.loc[z, 'a'] = a
                    result.loc[z, 'b'] = b
                    result.loc[z, 'c'] = c
                    result.loc[z, 'T'] = str(ctime - atime).replace('.', ',') #чтобы не выводились даты
                    z += 1
                    i = k
                else:
                    i = j
            else:
                i = j
        else:             
            i += 1
    return spo2, result


# график
# data = spo2['data'][:2000]
# t = spo2['n'][:2000]

# fig, axs = plt.subplots(3, 1, gridspec_kw={'height_ratios': [5, 1, 1]})
# axs[0].set_xlim(116160, 118160)
# axs[1].set_xlim(116160, 118160)
# axs[2].set_xlim(116160, 118160)

# axs[0].plot(t, data)
# axs[1].scatter(result['ibeg_time'][1], 1)
# for i in range(1, len(result)):
#     axs[1].add_patch(
#         patches.Rectangle(
#             xy = (int(result['ibeg_time'][i]), 1),
#             height = 0.1,
#             width = int(result['iend_time'][i] - result['ibeg_time'][i]),
#             edgecolor = 'blue',
#             fill = False
#         ))

# axs[2].scatter(spo2_ref['ibeg'][1], 1)
# for i in range(1, 18):
#     axs[2].add_patch(
#         patches.Rectangle(
#             xy = (int(spo2_ref['ibeg'][i]), 1),
#             height = 0.1,
#             width = int(spo2_ref['iend'][i] - spo2_ref['ibeg'][i]),
#             edgecolor = 'red',
#             fill = False
#         ))

# plt.show()