# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 11:57:42 2018

@author: gvg
"""

from datetime import datetime
import numpy as np
# from pydoc import locate
# import struct
# import os

def defaultInfo():
    mydict = {
        'ChCount' : 1, 
        'Fs' : -1.0,
        'LSB' : 1.0,
        'Precision' : np.int,
        'iBeg' : 0,
        'iEnd' : 0,
        'StartDateNum' : datetime.strptime('2000-01-01T00:00:00', '%Y-%m-%dT%H:%M:%S'),
        'ChNames' : ['Data1'],
        'ChLSB' : 1.0,
        'ChUnits' : ['unit'],                                                  
    }
    return mydict

def string2type(string):
    if (string == 'int32') | (string == 'long') :
        return (np.int)
    elif (string == 'int64') :
        return (np.int64)
    elif (string == 'float') :
        return (np.float32)
    elif (string == 'double') | (string == 'float64') :
        return (np.float64)
    return (np.int) # по умолчанию

def readHeader(filepath):
    info = defaultInfo()
    with open(filepath, 'r') as f:
        lines = f.read().splitlines()
        
        line = lines[0].split(' ');
        info['ChCount'] = int(line[0])
        info['Fs'] = float(line[1])
        info['LSB'] = float(line[2])
        if len(line) > 3:
            info['Precision'] = string2type(line[3])
            
        line = lines[1].replace(' ', '\t').split('\t');
        info['iBeg'] = int(line[0])
        info['iEnd'] = int(line[1])
        info['StartDateNum'] = datetime.strptime(line[2], '%Y-%m-%dT%H:%M:%S')
        
        info['ChNames'] = lines[2].split('\t')
        info['ChLSB'] = lines[3].rstrip().split('\t')
        info['ChUnits'] = lines[4].rstrip().split('\t')
        
        f.close()
    return info

dt = np.dtype([('time', [('min', int), ('sec', int)]), ('temp', float)])

def readBinFile(filepath):
    ext = filepath[len(filepath)-3:len(filepath)]
    binfile = filepath.replace(ext, 'bin')
    hdrfile = filepath.replace(ext, 'hdr')
    info = readHeader(hdrfile)
    
    # хорошо - здесь можно задавать разные типы!
    types = np.dtype(list(zip(info['ChNames'], [info['Precision']] * info['ChCount']))) # список кортежей имя-тип
    
    f = open(binfile, "rb")  # reopen the file
    arr = np.fromfile(f, dtype=types)  # read the data into numpy
    f.close()
    
    return info, arr

###############################################################################
###############################################################################
###############################################################################

# foldpath = 'D:\ЮЛЯ\!ИНКАРТ\Data\AllDataBases\БазаНов\KT-07_Испытания_здоровые\E6109150203113747.alg'
#  # путь к папке
# curFile='\params_ReoSmooth_2.hdr' #путь к конкретному файлу в ней/ надо указывать тот, что с разрешением  hdr
# filepath=foldpath+curFile 
# info, data = readBinFile(filepath)

# n_f=len(info['ChNames']) #количество каналов
# Param=np.zeros([len(data),n_f])
# for i in range(n_f):
#     Param[:,i]=data[info['ChNames'][i]] #для удобства делаем обычный массив

# #чтобы проверить, что все загрузило, построим график одного из отведений
# import matplotlib.pyplot as plt
# x = data['T_Ap'] 

# plt.plot(x)
# plt.ylabel('T_Ap')
# plt.show()
