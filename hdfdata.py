import h5py    
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

#1
def hdf_read(foldpath, curFile):

    f = h5py.File(foldpath + '\\' + curFile + '.hdf','r+') 

    # sleep ibeg and iend
    ibeg = int(f['Mark']['Sleep']['iBeg'][:])
    iend = int(f['Mark']['Sleep']['iEnd'][:])

    # spo2
    Fs_spo2 = float(f['Mark']['SPO2'].attrs['Freq'])
    type_spo2 = np.array(f['Mark']['SPO2']['Auto']['Type'][:])
    ibeg_spo2 = np.array(f['Mark']['SPO2']['Auto']['iBeg'][:]) / (Fs_spo2 / 2)
    iend_spo2 = np.array(f['Mark']['SPO2']['Auto']['iEnd'][:]) / (Fs_spo2 / 2)

    # reo

    Fs_reo = float(f['Mark']['Reo_0'].attrs['Freq'])
    type_reo = np.array(f['Mark']['Reo_0']['Auto']['Type'][:])
    ibeg_reo = np.array(f['Mark']['Reo_0']['Auto']['iBeg'][:]) 
    iend_reo = np.array(f['Mark']['Reo_0']['Auto']['iEnd'][:]) 

    f.close()

    #reo
    reo_ref = pd.DataFrame({
        'ibeg' : ibeg_reo,
        'iend' : iend_reo
    })

    #spo2
    spo2_ref = pd.DataFrame({
        'ibeg' : ibeg_spo2,
        'iend' : iend_spo2,
        'type' : type_spo2
    })
    spo2_ref = spo2_ref.drop(spo2_ref[spo2_ref.type != 2].index) 

    spo2_ref.insert(0, "id", range(1, int(len(spo2_ref) + 1))) 
    spo2_ref = spo2_ref.set_index('id')

    #reo 
    reo_ref = pd.DataFrame({
        'ibeg' : ibeg_reo,
        'iend' : iend_reo,
        'type' : type_reo
    })

    reo_ref = reo_ref.drop(reo_ref[(reo_ref.type != 2) & (reo_ref.type != 10)].index) 

    reo_ref.insert(0, "id", range(1, int(len(reo_ref) + 1))) 
    reo_ref = reo_ref.set_index('id')

    return Fs_reo, Fs_spo2, reo_ref, spo2_ref, ibeg, iend