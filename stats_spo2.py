import time
start_time = time.time()
import pandas as pd
import numpy as np
from hdfdata import hdf_read
from spo2 import spo2_desat
pd.options.mode.chained_assignment = None

foldpath = 'C:\\Users\\thewi\\OneDrive\\Рабочий стол\\incart_github\\incart\\breath_apnea_2' #путь к файлу без имени самого файла

with open(foldpath + '\\' + 'files.txt') as files: #открываем текстовый файл с названиями файлов
    list = [line.strip() for line in files]

results = {'stats': ['accuracy', 'sensitivity', 'specifity', 'prediction']}

for curfile in list:
    curFile = curfile #имя у всех трех файлов должно быть одинаковым

    Fs_reo, Fs_spo2, reo_ref, spo2_ref, ibeg, iend = hdf_read(foldpath, curFile)
    spo2, result = spo2_desat(foldpath, curFile)

    # таблица с отсчетами десатурации для референтной разметки
    ref_desat = np.arange(int(spo2_ref['ibeg'][1]), int(spo2_ref['iend'][1]) + 1)
    for i in range(2, len(spo2_ref) + 1):
        ref_desat = np.append(ref_desat, np.arange(int(spo2_ref['ibeg'][i]), int(spo2_ref['iend'][i]) + 1))
    ref_desat = np.array(ref_desat)

    # цикл для проставления 0 и 1 в отсчеты сигнала c референтной разметки
    spo2['ref_desat'] = [0] * len(spo2)
    for i in ref_desat:
        ind = spo2['n'][spo2.n == i].index[0]
        spo2['ref_desat'][ind] = 1

    #таблица с отсчетами десатурации для тестовой разметки
    test_desat = np.arange(int(result['ibeg_time'][1]), int(result['iend_time'][1]))
    for i in range(2, len(result)):
        test_desat = np.append(test_desat, np.arange(int(result['ibeg_time'][i]), int(result['iend_time'][i]) + 1))
    test_desat = np.array(test_desat)

    # цикл для проставления 0 и 1 в отсчеты сигнала c тестовой разметки
    spo2['test_desat'] = [0] * len(spo2)
    for i in test_desat:
        ind = spo2['n'][spo2.n == i].index[0]
        spo2['test_desat'][ind] = 1

    # цикл для расчета параметров
    spo2['result'] = [0] * len(spo2)

    for i in range(len(spo2)):
        if spo2['ref_desat'][i] == 1 and spo2['test_desat'][i] == 1:
            spo2['result'][i] = 'TP'
        elif spo2['ref_desat'][i] == 1 and spo2['test_desat'][i] == 0:
            spo2['result'][i] = 'FN'
        elif spo2['test_desat'][i] == 1 and spo2['ref_desat'][i] == 0:
            spo2['result'][i] = 'FP'
        elif spo2['test_desat'][i] == 0 and spo2['ref_desat'][i] == 0:
            spo2['result'][i] = 'TN'

    TP = (spo2.result == 'TP').sum()
    TN = (spo2.result == 'TN').sum()
    FN = (spo2.result == 'FN').sum()
    FP = (spo2.result == 'FP').sum()
    accuracy = np.around((TP + TN) / (TP + TN + FP + FN), decimals = 4)
    sensitivity = np.around(TP / (TP + FN), decimals = 4)
    specifity = np.around(TN / (TN + FP), decimals = 4)
    prediction = np.around(TP / (TP + FP), decimals = 4)
    # spo2.loc[0, 'accuracy'] = accuracy
    # spo2.loc[0, 'sensitivity'] = sensitivity
    # spo2.loc[0, 'specifity'] = specifity
    # spo2.loc[0, 'prediction'] = prediction
    results[curfile] = [accuracy, sensitivity, specifity, prediction]
results_spo2 = pd.DataFrame(results)
print(results_spo2)
print("--- %s seconds ---" % (time.time() - start_time)) #время работы программы
results_spo2.to_csv(foldpath + '\\' + 'results_spo2.csv', sep = ';') # запись результатов в .csv файл в папку с исходными файлами