
#------- This script englobes multiple sub functions whose primary goal is to treat Jsc vs Wavelength lists --------------------------------------------------------------------------------
#------- When importing a suggested notation is: import Jsc_From_EQE as JfE ----------------------------------------------------------------------------------------------------------------

import List_Finder as lstf                                                                                                      # We import necessary local functions that will be used in this script
import Small_Functions as sf
import time


# Function that returns a list of Jsc per nm from an EQE curve and a solar Data curve. The Solar data curve has to be more extensive than the EQE data curve
def Jsc_per_nm_list_from_EQE(EQE_Data,Solar_Data):                                                                              # The function needs two 2-D lists containing the EQE data (wavelength and EQE values) and the Solar irradiance spectrum data

    #First we declare some variables to be used later
    Jsc = 0                                                                                                                     # We define the Jsc variable
    Jsc_per_nm_list = list()                                                                                                    # We define the Jsc list where we will store all our values of interest
    Previous_Lambda = EQE_Data[0][0] - (EQE_Data[1][0]-EQE_Data[0][0])                                                          # We define the First lambda to calculate the Lambda differential as being one Lambda differential (EQE_Data[1][0]-EQE_Data[0][0]) below the first lambda value.

    # Now we loop through the data calculating the Jsc contribution of each EQE lambda differential
    for EQE_Data_row in EQE_Data:                                                                                               # For loop that iterates through every element within the EQE_Data list                                                                                                             # Afterwards, when First_append is no longer True, we start to extract the variables that we need for the calculation
        Current_Lambda = EQE_Data_row[0]                                                                                        # We set the Current_Lambda variable with the value of lambda extracted from the current row
        Current_EQE = EQE_Data_row[1]                                                                                           # We set the Current_EQE variable with the EQE value also extracted from the current row

        Solar_radiance = Solar_Data[(lstf.find_closest(Current_Lambda, Solar_Data))][1]                                         # The solar radiance is extracted from the Solar_Data variable and, to find it, what we do is we take the Current_Lambda and we search for the closest matching Lambda within
        # the Solar_Data list (since Solar_Data is much more extensive than any EQE we can measure, we can be sure that the closest lambda will be within 0.5 nm)
                                                                                                                                # With the index of that lambda (which becomes the first index) we extract the solar radiance (stored in the first column hence the [1]) at that wavelength
        Lambda_differential = Current_Lambda - Previous_Lambda                                                                  # Here we calculate the width in lambda (the Lambda_differential) to be used in the following pseudointegration
        #print('EQE = ' + str(EQE) + '  D_lambda = '  + str(d_lambda) + '  Solar Radiance = '  +str(Solar_radiance))            # The current line is just a print for debugging purposes
        Jsc = (0.01*Current_EQE*Lambda_differential*Solar_radiance*Current_Lambda/1240)                                         # Here we calculate the Jsc contribution of this particular section of the spectrum. The current Jsc block consists of the EQE turned into a unitary value (representing the height)
                                                                                                                                # the lambda difference (representing the width), the solar radiance at the current wavelength and the current lambda divided by 1240, to convert to eV, alltogether to convert to Jsc..
        Jsc_per_nm_list.append([Current_Lambda,round(Jsc,3)])                                                                   # We append the individual contribution of this part of the spectrum to the Jsc_list variable
        Previous_Lambda = Current_Lambda                                                                                        # We store the new lambda into the prev_lambda variable for the next iteration

    return Jsc_per_nm_list                                                                                                      # Finally we return the list with all the Jsc/nm values that is basically composed of all the individual contributions of the Jsc at different slices of the sun spectrum


# This function takes a Jsc list per nm and given a Voc and FF value it transforms it into its equivalent Eff_fer_nm list
def Per_nm_Jsc_to_Per_nm_Eff(Per_nm_Jsc_list,Voc,FF):                                                                       # This function takes a Per_nm_Jsc list a Voc value and a FF value in the form of a percentage
    Per_nm_Efficiency_list = list()                                                                                         # We first initialize the Per_nm_Efficiency_list that will hold the values of the efficiency per wavelength differential

    # Now we loop through all the Per_nm_Jsc_list taking each value and converting it to Per_nm_Eff value and appending it to the Per_nm_Eff_list
    for Jsc_value in Per_nm_Jsc_list:                                                                                       # For each Jsc value in the Per_nm_Jsc_list
        Eff_value = Jsc_value[1]*Voc*FF/100                                                                                 # We calculate the correspondent efficiency value by multiplying the Jsc, Voc and FF
        Per_nm_Efficiency_list.append([Jsc_value[0],Eff_value])                                                             # Once we have the efficiency value we append it to the list with its corresponding wavelength
    return Per_nm_Efficiency_list                                                                                           # Finally we return the list

# This function takes an arbitrary 1D Jsc list and given a Voc and FF value it transforms it into its equivalent arbitrary 1D Efficiency list. The main distinction with the former function is that this one takes any Jsc list that is one dimensional so each Jsc value does not need to be related to any wavelength
def Jsc_list_1D_to_Eff_list_1D(Jsc_list_1D,Voc,FF):                                                                         # This function takes a Jsc_list_1D list a Voc value and a FF value in the form of a percentage
    Efficiency_list_1D = list()                                                                                             # We first initialize the Efficiency_list_1D that will hold the values of the Efficiency for each Jsc value
    # print(Jsc_list_1D)
    # Now we loop through all the Jsc_list_1D taking each value and converting it to an Efficiency value and appending it to the Efficiency_list_1D
    for Jsc_value in Jsc_list_1D:                                                                                           # For each Jsc_value in the Jsc_list_1D
        Eff_value = Jsc_value*Voc*FF/100                                                                                    # We calculate the correspondent efficiency value by multiplying the Jsc, Voc and FF
        Efficiency_list_1D.append(Eff_value)                                                                                # Once we have the efficiency value we append it to the Efficiency_list_1D
    return Efficiency_list_1D                                                                                               # Finally we return the list

# Function that given a Jsc_per_nm_list will integrate the individual Jsc values within a given range and return the total Jsc contribution of that wavelength range
def integrate_Jsc(Jsc_per_nm_list,Start_wavelength,Stop_wavelength):                                                            # The function needs one 2-D list containing the Jsc_per_nm data (wavelength and Jsc values) and two wavelengths that define the integration range

    # First we find the start and stop wavelengths within the Jsc_per_nm_list to set the integration range within the array
    # and we declare the found indices as variables as well as declaring other variables of interest
    Start_index = lstf.find_closest(Start_wavelength, Jsc_per_nm_list,0, 10)                                                    # We first search for the closest wavelength value, within the Jsc_per_nm_list, to the specified Start_wavelength. If there is, at least, a lambda value that is
                                                                                                                                # closer than 10 nm to the Start_wavelength value we set the index of that lambda value (the position within the array) as the Start_index.
    Stop_index = lstf.find_closest(Stop_wavelength,Jsc_per_nm_list,0, 10)                                                       # We repeat the process for the Stop_index. If there is not any value that is at least 10 nm close to the Stop_wavelength value the index will be set to -1.
    Jsc = 0                                                                                                                     # We declare the Jsc variable

    # print('Start wavelength = '+str(Start_wavelength)+'   Start index = '+str(Start_index))                                   # Prints for debugging
    # print('Stop wavelength = ' + str(Stop_wavelength) + '   Stop index = ' + str(Stop_index))
    # print('-----')

    # We check if the start and stop wavelengths are within the data range and if they are we integrate the Jsc contributions
    # within that range
    if Start_index  != -1 and Stop_index != -1 :                                                                                # If none of the indexes is set to -1, hence the Start_wavelength and Stop_wavelength values are present, with a 10 nm tolerance, within the Jsc_per_nm_list
                                                                                                                                # it means that we will be able to perform the calculation hence we proceed.
        for i in range(Start_index,Stop_index):                                                                                 # For looping through the indicated range, from the start wavelength (which will be in the Start_index) to the stop wavelength (which will be in the Stop_index)
            Jsc = Jsc + Jsc_per_nm_list[i][1]                                                                                   # Basically add the current Jsc slice contribution (Jsc_per_nm_list[i][1]) to the total Jsc and set the Jsc to this new value. (Integration for dummies)
        # print('Jsc = '+str(Jsc)+'   Range = '+str(range(Start_index,Stop_index))+'  Length list = '+str(len(Jsc_per_nm_list)))
        # print('-------')
        return Jsc                                                                                                              # The function returns a numeric value with the integrated Jsc over the selected spectrum
    else:                                                                                                                       # If some of the indexes are indeed -1 it means that the range we have selected to calculate the Jsc is wider than the actual data we have available
        if Start_index == -1:                                                                                                   # If the Start_index is -1 it means the out of range condition happened due to Start_wavelength being too low
            print('Error: Start wavelength too low. Out of current file range by more than 10')                                 # In that case we print an error saying that the start wavelength was to low
        if Stop_index == -1:                                                                                                    # If the Stop_index is -1 it means the out of range condition happened due to Stop_wavelength being too high
            print('Error: Stop wavelength too high. Out of current file range by more than 10')                                 # In that case we print an error saying that the start wavelength was to high
        else:                                                                                                                   # This condition should not be possible but just in case we write an error for it
            print("Error: No idea what went wrong, but something did within the Integrate_Jsc function. Sorry :')")
        return -1                                                                                                               # The function returns a -1 if there has been a mistake

# --------------------------------------------------------------------------------------------- JfE tester program, uncomment if you want to debug this script: ---------------------------------------------------------------------------------------------------

import Jsc_From_EQE as JfE
import Text_Importer as txtImp
from tkinter import filedialog
import os

if __name__ == '__main__':

    EQE_TXT = filedialog.askopenfilename(title='Select the First EQE TXT you want to analyze',initialdir=os.getcwd(), filetypes=(('txt files','*.txt'),('All files','*.*')))        # Prompt the user to open a file that contains the EQE txt files, and assign the file path to the variable EQE_TXT_1
    EQE_Data = txtImp.import_txt(EQE_TXT)                          # Import the EQE data into the EQE_Data_1 Variable
    # print(*EQE_Data, sep='\n')                                          # For debugging purposes


    Solar_TXT = filedialog.askopenfilename(title='Select the Solar Curve Spectrum TXT ',initialdir=os.getcwd(), filetypes=(('txt files','*.txt'),('All files','*.*')))   # Prompt the user to open a file that contains the Solar Curve txt files, and assign the file path to the variable Solar_TXT
    Solar_Data = txtImp.import_txt(Solar_TXT)                        # Import the Solar curve data into the Solar_Data Variable
    # print(*Solar_Data, sep='\n')                                          # For debugging purposes


    foo = JfE.Jsc_per_nm_list_from_EQE(EQE_Data,Solar_Data)
    print(*foo,sep='\n')

    foo = JfE.integrate_Jsc(foo,400,600)
    print(foo)

########################################################---------------------------------------------- Uncomment until here to test the script ---------------------------------------------------############################################################################################

# ---------------------------------------------------------------------------------------------------------- Old deprecated functions -----------------------------------------------------------------------------------------------------------------------------------------------------------

# def Jsc_from_EQE(EQE_Data,Solar_Data,Start_wavelength,Stop_wavelength):
#     line_count = 0
#     Jsc = 0
#     for i in range(lstf.find_closest(Start_wavelength,EQE_Data),lstf.find_closest(Stop_wavelength,EQE_Data)):                 # For loop that first finds the range in which you want to calculate the Jsc from the EQE taking into account the Start_wavelength and Stop_Wavelength parameters
#         if line_count==0:                                                                                                     # and then calculates the Jsc contribution from that range
#             prev_lambda = EQE_Data[i][0]                                                                                      # Store the previous lambda for the computation of the lambda differential (d_lambda) needed for the main calculation
#             line_count+= 1;                                                                                                   # If line_count is equal to 0 we just store the first lambda information since we cannot use a constant for that information, it is always relative.
#         else :                                                                                                                # Afterwards, when line_count is no longer 0, we start to extract the variables that we need for the calculation
#             Solar_radiance = Solar_Data[(lstf.find_closest(EQE_Data[i][0], Solar_Data))][1]                                   # The solar radiance is extracted from the Solar_Data variable and, to find it, what we do is we take the current EQE wavelength (EQE_Data[i][0]) and we
#             EQE = EQE_Data[i][1]                                                                                              # search for the closest within the Solar_Data list (since Solar_Data is much more extensive than any EQE we can measure, we can be sure that the closest lambda
#             d_lambda = EQE_Data[i][0]-prev_lambda                                                                             # will be within 0.5 nm). With the index of that lambda we extract the solar radiance at that wavelength. On the next line we just store the EQE value for that
#             #print('EQE = ' + str(EQE) + '  D_lambda = '  + str(d_lambda) + '  Solar Radiance = '  +str(Solar_radiance))      # wavelength and on the next one we calculate the difference in lambda from the previous one. (The current line is just a print for debugging purposes)
#             Jsc = Jsc + (0.01*EQE*d_lambda*Solar_radiance*EQE_Data[i][0]/1240)                                                # Here we calculate the Jsc by adding the previous "carried on" Jsc to the current "Jsc block". The current Jsc block consists of the EQE turned into a unitary value
#                                                                                                                               # the lambda difference, the solar radiance at the current wavelength and the current lambda divided by 1240 to convert to eV.
#             prev_lambda = EQE_Data[i][0]                                                                                      # We store the new lambda into the prev_lambda variable for the next iteration
#             line_count += 1;                                                                                                  # Increase the counter (not entirely necessary)
#             # print(type(in_list(round(EQE_Data[i][0]),Solar_Data)))                                                          # For Debugging purposes
#     Jsc = round(Jsc,3)                                                                                                        # Round the Jsc to 3 decimals
#     #print('Jsc = ' + str(Jsc) + ' mA / cm^2')                                                                                # Print Jsc (for debugging purposes)
#     return Jsc