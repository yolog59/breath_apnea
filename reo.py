from BinFileUtils import readBinFile 
from hdfdata import hdf_read
from peak_detection import peakdet
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.patches as patches
from butterworth_filter import butter_bandpass_filter

def reo_find(foldpath, curFile):
        filepath = foldpath + '\\' + curFile + '.hdr'
        info, data = readBinFile(filepath)
        Fs_reo, Fs_spo2, reo_ref, spo2_ref, ibeg, iend = hdf_read(foldpath, curFile)

        #reo
        Fs = int(info['Fs'])
        k = Fs / Fs_reo
        data = np.array(data['Reo'])
        t_counts = np.arange(ibeg, iend)

        ibeg_data = int(info['iBeg'])
        iend_data = int(info['iEnd'])
        ibeg_diff = int(ibeg - ibeg_data / k)
        iend_diff = int(iend_data / k - iend)

        # из-за прореживания частоты дискретизации, убираем лишние отсчёты
        data = data[::int(k)]
        data = data[ibeg_diff : iend - ibeg + ibeg_diff]

        # пропускаем сигнал через фильтр Баттерворта
        data = butter_bandpass_filter(data, 0.05, 1, 32.125)
        # print(data)

        # исходные данные
        dict = {
                'data' : data,
                'n' : t_counts
        }
        reo = pd.DataFrame(dict)

        # somedata = reo[0:20000]
        # somedata.insert(0, "id", range(1, int(len(somedata) + 1))) 
        # somedata = somedata.set_index('id')

        # находим пики 
        max, min = peakdet(reo, 100)

        # таблица для работы с размахом
        result_dict = {
                'max_ncount' : max[:,0],
                'max' : max[:,1],
                'min_ncount' : min[:,0],
                'min' : min[:,1],
                'magnitude' : 0,
        }
        result = pd.DataFrame({key : pd.Series(value) for key, value in result_dict.items()})

        i = 0
        j = 0

        # вычисление размахов для следующего цикла
        while i + 1 < len(result) or j + 1 < len(result):
                if result['max_ncount'][i] < result['min_ncount'][j]:
                        i += 1
                        continue
                # if result['min'][j + 1] == np.nan:
                #         break
                min_average = (abs(result['min'][j]) + abs(result['min'][j + 1])) / 2
                magnitude = abs(result['max'][i] - min_average)
                result.loc[i, 'magnitude'] = magnitude
                i += 1
                j += 1
                # z += 1
        #таблица для записи начала и конца событий
        result_test = pd.DataFrame()

        # цикл для поиска периодов апноэ и гипапноэ
        i = 0
        z = 0
        while i + 1 < len(result):
                counter = 0
                time_limit = 0
                if result['magnitude'][i] == 0:
                        i += 1
                        continue
                elif result['max_ncount'][i + 1] - result['max_ncount'][i] > 10 * Fs_reo: #апноэ
                        time_limit = result['max_ncount'][i + 1] - result['max_ncount'][i]
                        type = 'apn'
                        result.loc[j, 'ibeg'] = ibeg 
                        result.loc[i, 'iend'] = result['max_ncount'][i]
                        result.loc[i, 'T'] = (result['max_ncount'][i] - result['max_ncount'][j]) / Fs_reo 
                        result_test.loc[z, 'ibeg'] = ibeg 
                        result_test.loc[z, 'iend'] = result['max_ncount'][i]
                        result_test.loc[z, 'T'] = (result['max_ncount'][i] - result['max_ncount'][j]) / Fs_reo
                        result_test.loc[z, 'type'] = type 
                        i += 1
                        z += 1
                elif result['magnitude'][i + 1] < 0.8 * result['magnitude'][i]: #гипапноэ
                        j = i
                        first = result['magnitude'][j]
                        ibeg = result['max_ncount'][j]
                        i += 1
                        time_limit = 0
                        if i + 1 > len(result) - 1:
                                break
                        if result['max_ncount'][i + 1] - result['max_ncount'][i] > 10 * Fs_reo: #апноэ внутри гипапноэ
                                time_limit = result['max_ncount'][i + 1] - result['max_ncount'][i]
                                type = 'apn'
                        elif result['magnitude'][i] < 0.9 * first:
                                while result['magnitude'][i] < 0.9 * first: #гипапноэ
                                        time_limit += result['max_ncount'][i] - result['max_ncount'][i - 1]
                                        i += 1
                                        counter += 1
                                        if i + 1 > len(result) - 1:
                                                i -= 1
                                                break
                                        if result['max_ncount'][i + 1] - result['max_ncount'][i] > 10 * Fs_reo: #апноэ внутри гипапноэ
                                                type = 'apn'
                                                break
                                        type = 'hypop'
                        if time_limit > 10 * Fs_reo and time_limit < 180 * Fs_reo or (counter >= 3 and time_limit > 10 * Fs_reo and time_limit < 180 * Fs_reo): #счетчик дыхательных циклов для гипапноэ, счетчик секунд - для апноэ
                                result.loc[j, 'ibeg'] = ibeg 
                                result.loc[i, 'iend'] = result['max_ncount'][i]
                                result.loc[i, 'T'] = (result['max_ncount'][i] - result['max_ncount'][j]) / Fs_reo 
                                result_test.loc[z, 'ibeg'] = ibeg 
                                result_test.loc[z, 'iend'] = result['max_ncount'][i]
                                result_test.loc[z, 'T'] = (result['max_ncount'][i] - result['max_ncount'][j]) / Fs_reo
                                result_test.loc[z, 'type'] = type 
                                z += 1
                        elif time_limit > 180 * Fs_reo:
                                i = j + 1
                                time_limit = 0
                else:
                        i += 1
        return reo, result_test


#график
# t = reo['n']
# fig, axs = plt.subplots(3, 1, gridspec_kw={'height_ratios': [5, 1, 1]})
# axs[0].set_xlim(1870000, 2910000)
# axs[1].set_xlim(1870000, 2910000)
# axs[2].set_xlim(1870000, 2910000)

# axs[0].plot(t, data)
# axs[1].scatter(result_test['ibeg'][1], 1)
# for i in range(1, len(result_test)):
#         if result_test['type'][i] == 'hypop':
#                 axs[1].add_patch(
#                 patches.Rectangle(
#                 xy = (int(result_test['ibeg'][i]), 1),
#                 height = 0.1,
#                 width = int(result_test['iend'][i] - result_test['ibeg'][i]),
#                 edgecolor = 'blue',
#                 fill = False
#                 ))
#         elif result_test['type'][i] == 'apn':
#                 axs[1].add_patch(
#                 patches.Rectangle(
#                 xy = (int(result_test['ibeg'][i]), 1),
#                 height = 0.1,
#                 width = int(result_test['iend'][i] - result_test['ibeg'][i]),
#                 edgecolor = 'green',
#                 fill =  False))

# axs[2].scatter(reo_ref['ibeg'][1], 1)
# for i in range(1, len(reo_ref)):
#     axs[2].add_patch(
#         patches.Rectangle(
#             xy = (int(reo_ref['ibeg'][i]), 1),
#             height = 0.1,
#             width = int(reo_ref['iend'][i] - reo_ref['ibeg'][i]),
#             edgecolor = 'red',
#             fill = False
#         ))
# plt.show()