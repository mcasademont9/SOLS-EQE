
# ------------------------------ The main function of this script is to extract some parameters of interest from a JV curve, namely the Voc, Jsc and FF
# ------------------------------ The recommended import method is the following: import JV_Parameters_From_JV_Curve as JV_Par

import List_Finder as lstf                                                                                                  # Import all necessary scripts and libraries
import Small_Functions as sf
from statistics import mean

# This function calculates the Voc, the Jsc and the FF from a Jv curve. To do so, it searches for the point of 0V and averages the current points in that region and analogously it searches for the point of 0 current and averages the voltage values around that point.
# To calculate the FF it searches for the maximum generated power point and calculates the division between the maximum theoretical power (Jsc*Voc) and the maximum real power (Vmp*Jmp).
def JV_Par_from_JV_curv(JV_Curve,points_for_fit = 10):                                                                      # This function takes a JV curve as a required field and an optional field, the points_for_fit that are used for the averaging

    # First we find the Jsc. For that we search on the JV curve where the voltage is 0 (lstf.find_closest(0,JV_Curve,0,1)) this will return the index where it finds the
    # closest voltage to 0. For that it searches for the closest value to 0 within the JV curve with a max tolerance of 1V (as of now, it seems a bit much but it works)
    # and then it sets the Jsc index to that where the value of the voltage is as close to zero as possible.
    Jsc_index = lstf.find_closest(0,JV_Curve,0,1)                                                                           # To search for the value that is closest to zero, it uses the function lstf.find_closest() that is further described in the List_finder Script

    Jsc_low_index_fit = int((Jsc_index - (points_for_fit / 2)))                                                             # For a better Jsc fit we set an interval to make an average of the Jsc to reduce noise. Here we declare the lowest index of the interval.
    Jsc_high_index_fit = int((Jsc_index + (points_for_fit / 2)))                                                            # And here we declare the highest index. These indexes can be changed via the points_for_fit parameter.
    Jsc_Fit = sf.Extract_Column(JV_Curve[Jsc_low_index_fit:Jsc_high_index_fit],1)                                           # We extract the J values that are close to the Jsc value, and place them into the Jsc_Fit list.
    #print(Jsc_Fit)                                                                                                         # Print Jsc_Fit For debugging purposes,
    mean_Jsc = mean(Jsc_Fit)                                                                                                # We average the J values around the exact Jsc value to obtain a signal less susceptible to noise

    # We repeat the same procedure for the Voc but in this case we set a higher tolerance of 2 (still higher than needed in my opinion). We search for that value on
    # column one. And once found we set the index of that value as the Voc index
    Voc_index = lstf.find_closest(0,JV_Curve,1,2)                                                                           # To search for the value that is closest to zero, it uses the function lstf.find_closest() that is further described in the List_finder Script
    Voc_low_index_fit = int((Voc_index - (points_for_fit / 2)))                                                             # Again we set a range of indices for better precision, here we set the lower Voc index
    Voc_high_index_fit = int((Voc_index + (points_for_fit / 2)))                                                            # Here we set the highest Voc index for the fit function
    Voc_Fit = sf.Extract_Column(JV_Curve[Voc_low_index_fit:Voc_high_index_fit],0)                                           # Here we extract the values around Voc in order to average them and reduce noise
    #print(Voc_Fit)                                                                                                         # Print Voc_Fit For debugging purposes
    mean_Voc = mean(Voc_Fit)                                                                                                # We average the Voc values to have a Voc less sensitive to noise

    # To prevent errors we also take the actual single Voc and Jsc value, that will be compared to the means of the values.
    Jsc = JV_Curve[lstf.find_closest(0,JV_Curve,0,1)][1]                                                                    # We also search for the actual value of the Voc and the Jsc
    Voc = JV_Curve[lstf.find_closest(0,JV_Curve,1,2)][0]                                                                    # We do that by finding again the closest value to 0 of each respective parameter and saving it into their corresponding variable
    if (abs(Voc-mean_Voc) >= 0.15) or (abs(Jsc-mean_Jsc) >= 0.5):                                                           # If the difference between the averaged values and the exact ones varies too much we discard the measurement and we
        print('Voc or Jsc calculus error')                                                                                  # print an error that tells us there has been an error when calculating the Jsc and Voc
        return -1                                                                                                           # If there is an error just return -1

    # This variable will hold the min power value, we could set it to anything with a high value because the power generated by solar cells is negative so whenever
    # it finds a lower value it will hold onto it.
    min_power = 99
    power = list()  # We define the list that will hold the power values

    # Now we loop through the Values in the JV_Curve to search for the maximum generated power value
    for value in JV_Curve:                                                                                                  # For each value in Jv_Curve
        power.append(value[0]*value[1])                                                                                     # We append the power of this particular point of the JV curve to the power list
        if min_power > (value[0]*value[1]):                                                                                 # If the current power value is lower than the min power value
            Vmp = value[0]                                                                                                  # We set the Vmp and the Jmp to the current J and V values
            Jmp = value[1]                                                                                                  # And we also set the min_power to the current power so that in the next iteration this will be the lowest power found, hence the one to compare against
            min_power = (value[0]*value[1])                                                                                 #
    FF = round(100*(Vmp*Jmp)/(Voc*Jsc),2)                                                                                   # The fill factor is calculated with the Vmp, Jmp, Voc, and Jsc and we give it as a percentage
    return abs(mean_Jsc),abs(mean_Voc),FF                                                                                   # The function returns the absolute values of Jsc, Voc and FF as three separate values

# --------------------------------------------------------------------------------------------- JV_Par tester program, uncomment if you want to debug this script: ---------------------------------------------------------------------------------------------------
#
# from tkinter import filedialog
# import Text_Importer as txtImp
# import os
#
# if __name__ == "__main__":
#     JV_curve_TXT = filedialog.askopenfilename(title='Select the JV curve TXT you want to analyze',initialdir=os.getcwd(), filetypes=(('txt files','*.txt'),('All files','*.*')))        # Prompt the user to open a file that contains the JV curve txt files, and assign the file path to the variable JV_curve_TXT
#     JV_curve_Data = txtImp.import_txt(JV_curve_TXT)                             # Import the JV curve data into the JV_curve_Data Variable
#     # print(*JV_curve_Data, sep='\n')                                                # For debugging purposes
#
#     Jsc, Voc, FF = JV_Par_from_JV_curv(JV_curve_Data)                           # Calculate the JV_curve parameters from the JV_curve data
#
#     print('Jsc = '+str(Jsc)+' mA * cm^-2')
#     print('Voc = '+str(Voc)+' V')
#     print('FF = '+str(FF)+' %')

########################################################---------------------------------------------- Uncomment until here to test the script ---------------------------------------------------############################################################################################