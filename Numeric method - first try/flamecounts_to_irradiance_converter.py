#This script contains all the necessary functions to convert a desired flame spectra (counts) into irradiance
#Recomended importing sequence: import flamecounts_to_irradiance_converter as fcTirr 

import numpy as np

def counts_to_irradiance(flame_data, integration_time, k_filepath):
    
    k_data = np.loadtxt(k_filepath,skiprows=1)
    flame_min_wavelength = min(flame_data[:,0])
    flame_max_wavelength = max(flame_data[:,0])
    flame_lines = len(flame_data[:,0])
    k_min_wavelength = min(k_data[:,0])
    k_max_wavelength = max(k_data[:,0])
    k_lines = len(k_data[:,0])


    if k_min_wavelength == flame_min_wavelength and k_max_wavelength == flame_max_wavelength and flame_lines == k_lines:
        irradiance = np.zeros(flame_data.shape)
        for i in range(len(irradiance[:,0])):
            irradiance[i,0] = flame_data[i,0]
            irradiance[i,1] = flame_data[i,1]*k_data[i,1]/integration_time
        
        return k_data
    
    else:
        return print('ERROR. The length of flame data array and k data array are not the same!')   


