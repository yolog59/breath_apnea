import time
start_time = time.time()
import pandas as pd
import numpy as np
from hdfdata import hdf_read
from reo import reo_find
from spo2 import spo2_desat
# from matplotlib import pyplot as plt
# import matplotlib.patches as patches
pd.options.mode.chained_assignment = None

foldpath = 'C:\\Users\\thewi\\OneDrive\\Рабочий стол\\incart_github\\incart\\breath_apnea_2' #путь к файлу без имени самого файла

with open(foldpath + '\\' + 'files.txt') as files: #открываем текстовый файл с названиями файлов
    list = [line.strip() for line in files]

results = {'stats': ['accuracy', 'sensitivity', 'specifity', 'prediction']}
for curfile in list:
    curFile = curfile #имя у всех трех файлов должно быть одинаковым

    Fs_reo, Fs_spo2, reo_ref, spo2_ref, ibeg, iend = hdf_read(foldpath, curFile)
    spo2, result = spo2_desat(foldpath, curFile)
    reo, result_test = reo_find(foldpath, curFile)

    desat_beg = np.array(result['ibeg_time'])
    desat_min = np.array(result['min_time'])
    desat_end = np.array(result['iend_time'])

    k = int(Fs_reo) / 2

    reo_ibeg = np.array(result_test['ibeg']) / k # приводим к отсчётам сатурации
    reo_iend = np.array(result_test['iend']) / k

    for i in range(len(reo_ibeg)):
        for j in desat_beg:
            if reo_ibeg[i] < j:
                if j - reo_ibeg[i] <= 80: # 40 секунд из статьи в отсчетах по 2 Гц
                    result_test.loc[i, 'result'] = '+' # если возможное апноэ/гипапноэ началось менее, чем за 40 секунд до десатурации, то присваиваем "+"
                    break
                else:
                    continue
            else:
                continue

    result_test = result_test.drop(result_test[result_test.result != '+'].index) # удаляем все значения без "+"
    result_test.insert(0, "id", range(1, int(len(result_test) + 1))) 
    result_test = result_test.set_index('id')
    result_test = result_test[1:]

    # сравнение с референтной разметкой
    ref_reo = np.arange(int(reo_ref['ibeg'][1]), int(reo_ref['iend'][1]) + 1)
    for i in range(2, len(reo_ref)): #len + 1
        ref_reo = np.append(ref_reo, np.arange(int(reo_ref['ibeg'][i]), int(reo_ref['iend'][i]) + 1))
    ref_reo = set(ref_reo)

    # цикл для проставления 0 и 1 в отсчеты сигнала c референтной разметки
    list_ref = []
    for i in set(reo['n']):
        if i in ref_reo:
            list_ref.append(1)
        else:
            list_ref.append(0)
    reo['ref_reo'] = list_ref

    #таблица с отсчетами десатурации для тестовой разметки
    test_reo = np.arange(int(result_test['ibeg'][2]), int(result_test['iend'][2]))
    for i in range(3, len(result_test)):
        test_reo = np.append(test_reo, np.arange(int(result_test['ibeg'][i]), int(result_test['iend'][i]) + 1))
    test_reo = set(test_reo)

    # цикл для проставления 0 и 1 в отсчеты сигнала c тестовой разметки
    list_test = []
    for i in set(reo['n']):
        if i in test_reo:
            list_test.append(1)
        else:
            list_test.append(0)
    reo['test_reo'] = list_test

    # цикл для расчета параметров
    result = []
    for i in range(len(reo)):
        if list_ref[i] == 1 and list_test[i] == 1:
            result.append('TP')
        elif list_ref[i] == 1 and list_test[i] == 0:
            result.append('FN')
        elif list_test[i] == 1 and list_ref[i] == 0:
            result.append('FP')
        elif list_test[i] == 0 and list_ref[i] == 0:
            result.append('TN')
    # reo['result'] = result

    TP = result.count('TP')
    TN = result.count('TN')
    FN = result.count('FN')
    FP = result.count('FP')
    accuracy = np.around((TP + TN) / (TP + TN + FP + FN), decimals = 4)
    sensitivity = np.around(TP / (TP + FN), decimals = 4)
    specifity = np.around(TN / (TN + FP), decimals = 4)
    prediction = np.around(TP / (TP + FP), decimals = 4)
    # reo.loc[0, 'accuracy'] = accuracy
    # reo.loc[0, 'sensitivity'] = sensitivity
    # reo.loc[0, 'specifity'] = specifity
    # reo.loc[0, 'prediction'] = prediction
    results[curfile] = [accuracy, sensitivity, specifity, prediction]
results_table = pd.DataFrame(results)
print(results_table)
print("--- %s seconds ---" % (time.time() - start_time)) # время работы программы (у меня вышло 106 секунд)
results_table.to_csv(foldpath + '\\' + 'results.csv', sep = ';') # запись результатов в .csv файл в папку с исходными файлами



#график
# t = reo['n']
# data = reo['data']
# fig, axs = plt.subplots(3, 1, gridspec_kw={'height_ratios': [5, 1, 1]})
# axs[0].set_xlim(2200000, 2250000)
# axs[0].set_ylim(-700, 800)
# axs[1].set_xlim(2200000, 2250000)
# axs[2].set_xlim(2200000, 2250000)

# axs[0].plot(t, data)
# axs[1].scatter(result_test['ibeg'][2], 1)
# for i in range(2, len(result_test)):
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