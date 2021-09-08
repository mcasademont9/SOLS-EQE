
# -------------------------------------------------------- This script main function is to search for the band gap within EQE curves
# -------------------------------------------------------- The recommended import method for this script is the following: import Bgap_Finder as BgF

import Small_Functions as sf                                                                                    # Import all necessary functions
import warnings


# This functions purpose is to extract an approximate band gap from any EQE curve. (This function is completely wrong and kept here to avoid failure of other scripts but it will be soon moved to deprecated files)
def Find_Bgap(EQE_Curve,Height_Ratio_Detection_Threshold = 0.2,Width_detection_threshold = 10):                 # It has 1 required input which is a 2d list containing an EQE curve (wavelength and EQE values). It also accepts 2 optional values, to calibrate the detection sinsitivity.
                                                                                                                # The first is at which height do we consider the EQE to be significant enough and the second is for how long does it need to be significant enough so that we decide that it is actually risen

    Detected_Values = 0                                                                                         # We initialize a counter which will hold the times the value has been above the threshold
    EQE_Max_Value = max(sf.Extract_Column(EQE_Curve,1))                                                         # We also extract the maximum EQE value from the list, which we will use to calculate the minimum threshold

    # Now we loop in reverse through all the EQE curve searching for the rising point. When we are sure that we have found it we return said value as the Band gap
    for i in reversed(range(len(EQE_Curve))):

        # If we detect that the current value is higher than the threshold we increase the counter value
        if (EQE_Curve[i][1] / EQE_Max_Value) >= Height_Ratio_Detection_Threshold:
            Detected_Values +=1

        # Otherwise we set the counter to 0 to erase false positives
        else:
            Detected_Values = 0

        # If the counter reaches the Width_detection_threshold value we consider this as the characteristic falling slope of the Bgap and we set the bgap value as the one with 20% the max EQE value
        if Detected_Values >= Width_detection_threshold:
            Bgap = round(EQE_Curve[i-10][0])
            return Bgap                                                 # We return the Bgap value
            break                                                       # We break the loop, it is not necessary but just in case

    # If the for loop finishes and there has not been a clair enough bgap value we print a warning and return -1
    warnings.warn('WARNING: No Bgap found for specified curve, check again the curve and the threshold parameters ')
    return -1

# --------------------------------------------------------------------------------------------- BgF tester program, uncomment if you want to debug this script: ---------------------------------------------------------------------------------------------------

import matplotlib.pyplot as plt
from tkinter import filedialog
import Text_Importer as txtImp
import os

if __name__ == '__main__':
    EQE_TXT_1 = filedialog.askopenfilename(title='Select the First EQE TXT you want to analyze', initialdir=os.getcwd(), filetypes=(('txt files', '*.txt'), ('All files', '*.*')))  # Prompt the user to open a file that contains the EQE txt files, and assign the file path to the variable EQE_TXT_1
    EQE_Data_1 = txtImp.import_txt(EQE_TXT_1)  # Import the EQE data into the EQE_Data_1 Variable

    print(Find_Bgap(EQE_Data_1))

########################################################---------------------------------------------- Uncomment until here to test the script ---------------------------------------------------############################################################################################