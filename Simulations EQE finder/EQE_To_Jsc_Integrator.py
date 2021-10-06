# -------------------------------- This script mainly contains functions whose primary function is to integrate EQE, Jsc or other variables
# -------------------------------- The suggested import method is the following: import EQE_To_Jsc_Integrator as EtJ

import time  # Import all necessary functions
import Jsc_From_EQE as JfE
import Small_Functions as sf


# This function takes two EQE curves, and a solar spectrum, and divides the spectrum between those two. With the divided spectrum it calculates the Jsc contribution of each cell and their added Jsc contribution.
# It calculates their Jsc contribution while varying the division wavelength along their whole spectrum to obtain a curve where we can see Jsc of either of the cells and total Jsc vs the dividing wavelength.
def EQE_vs_div_wavelength_curve(
    EQE_Data_1,
    EQE_Data_2,
    Solar_Data,  # This function needs Two EQE_Data lists that contain wavelength and EQE values in the shape of two columns. Also it needs a solar spectrum with the irradiance values
    Integrated_Jsc_correction_factor_1=1,
    Integrated_Jsc_correction_factor_2=1,
):  # It also takes two optional value which can correct the Jsc with the known Jsc value from each of the JV curves

    Timer1 = (
        sf.Timer()
    )  # We start the time to be able to count how long does it take to perform the operation. Now it takes almost nothing because it is more or less optimized
    # but it used to take almost 1 min so that is why we added this function. In this line we just declare the variable for the estimated time
    #
    First_EQE_wavelength = max(
        [EQE_Data_1[0][0], EQE_Data_2[0][0]]
    )  # We set the Wavelength range to be as short as the EQE data requires. For that we take the start wavelength to be the highest starting wavelength of both datasets
    Last_EQE_wavelength = min(
        [EQE_Data_1[-1][0], EQE_Data_2[-1][0]]
    )  # Similarly, we set the stop wavelength to be the lowest wavelength of both datasets, to prevent operations where one of the arrays would be empty
    #
    divide_lambda_list = (
        list()
    )  # We just define the arrays that will hold the dividing lambda parameter
    Jsc_sum_1 = list()  # The Jsc of the first cell
    Jsc_sum_2 = list()  # The Jsc of the second cell
    Jsc_total = list()  # The sum of both Jsc

    # We extract Jsc_per_nm data from each EQE curve
    EQE_Jsc_list_1 = JfE.Jsc_per_nm_list_from_EQE(
        EQE_Data_1, Solar_Data
    )  # We extract the Jsc per nm list from the first EQE data. We do this now because this step takes some time and we'd rather do it once and extract the data
    EQE_Jsc_list_2 = JfE.Jsc_per_nm_list_from_EQE(
        EQE_Data_2, Solar_Data
    )  # than have to do it for every loop iteration. We store the Jsc values into their respective lists for further use

    # Timer1.Update_elapsed_time(time.time())
    # print(Timer1.elapsed_time_precise_string+'First Step')
    # Now we loop through all possible dividing wavelengths while integrating each cell Jsc contribution
    for divide_lambda in range(
        int(First_EQE_wavelength), int(Last_EQE_wavelength)
    ):  # We initialize a for loop that will go from the first wavelength declared previously to the last wavelength

        divide_lambda_list.append(
            divide_lambda
        )  # We append our dividing lambda parameter to the divide_lambda_list so that we will keep track of the x axis for further plotting
        temp_Jsc1 = (
            JfE.integrate_Jsc(EQE_Jsc_list_1, int(First_EQE_wavelength), divide_lambda)
        ) * Integrated_Jsc_correction_factor_1  # We integrate the EQE_Jsc_list_1 from the starting wavelength to the current dividing wavelength and we store the obtained Jsc value on the temp_Jsc1 variable
        # We apply a correction factor to all Jsc values to make them closer to the true Jsc value extracted from the JV curves
        temp_Jsc2 = (
            JfE.integrate_Jsc(EQE_Jsc_list_2, divide_lambda, int(Last_EQE_wavelength))
        ) * Integrated_Jsc_correction_factor_2  # We integrate now the EQE_Jsc_list_2 from the dividing wavelength to the last wavelength and store the obtained Jsc on the temp_Jsc2 variable

        Jsc_sum_1.append(
            temp_Jsc1
        )  # We append the integrated Jsc value at the current dividing wavelength to the Jsc_sum_1 list
        Jsc_sum_2.append(temp_Jsc2)  # We do the same for the temp_Jsc2 value
        Jsc_total.append(
            (temp_Jsc1 + temp_Jsc2)
        )  # And for the total Jsc we just add the temporal values and append it to the Jsc_total list
        # Timer1.Update_elapsed_time()                                                                                      # We can keep track of the time it takes for each step to calculate
        # print(Timer1.elapsed_time_precise_string)
    return (
        divide_lambda_list,
        Jsc_sum_1,
        Jsc_sum_2,
        Jsc_total,
    )  # We finally return all the curves of interest as separate lists


# This function takes Per_nm_Efficiency_list and integrates the total efficiency of the cell from it
def Integrated_Eff(
    Per_nm_Efficiency_list,
):  # We need to provide a Per_nm_Efficiency_list with the Efficiency contribution at each wavelength differential
    Total_Efficiency = 0  # We first initialize the Efficiency variable that will hold the total efficiency value
    for (
        Eff_value
    ) in Per_nm_Efficiency_list:  # For each Eff_value within the Per_nm_Efficiency_list
        Total_Efficiency = (
            Total_Efficiency + Eff_value[1]
        )  # We add the current efficiency value to the whole efficiency. We are basically integrating the efficiency over the whole spectrum
    return Total_Efficiency  # We then return the Total_Efficiency value


# This function takes Per_nm_Jsc_list and integrates the total Jsc of the cell from it
def Integrated_Jsc(
    Per_nm_Jsc_list,
):  # This function needs a Per_nm_Jsc_list with the Jsc contribution at each wavelength differential
    Total_Jsc = 0  # We first initialize the Efficiency list that will hold the values
    for Jsc_value in Per_nm_Jsc_list:  # For each Jsc value in the Jsc_list
        Total_Jsc = (
            Total_Jsc + Jsc_value[1]
        )  # We calculate the correspondent efficiency value by multiplying the Jsc, Voc and FF
    return Total_Jsc  # We then return the Total_Jsc value


# --------------------------------------------------------------------------------------------- EtJ tester program, uncomment if you want to debug this script: ---------------------------------------------------------------------------------------------------

import Text_Importer as txtImp
from tkinter import filedialog
import EQE_To_Jsc_Integrator as EtJ
import os
import matplotlib.pyplot as plt

if __name__ == "__main__":

    EQE_TXT_1 = filedialog.askopenfilename(
        title="Select the First EQE TXT you want to analyze",
        initialdir=os.getcwd(),
        filetypes=(("txt files", "*.txt"), ("All files", "*.*")),
    )  # Prompt the user to open a file that contains the EQE txt files, and assign the file path to the variable EQE_TXT_1
    EQE_Data_1 = txtImp.import_txt(
        EQE_TXT_1
    )  # Import the EQE data into the EQE_Data_1 Variable
    # print(*EQE_Data, sep='\n')                                          # For debugging purposes

    EQE_TXT_2 = filedialog.askopenfilename(
        title="Select the Second EQE TXT you want to analyze",
        initialdir=os.getcwd(),
        filetypes=(("txt files", "*.txt"), ("All files", "*.*")),
    )  # Prompt the user to open a file that contains the EQE txt files, and assign the file path to the variable EQE_TXT_1
    EQE_Data_2 = txtImp.import_txt(
        EQE_TXT_2
    )  # Import the EQE data into the EQE_Data_1 Variable
    # print(*EQE_Data, sep='\n')                                          # For debugging purposes

    Solar_TXT = filedialog.askopenfilename(
        title="Select the Solar Curve Spectrum TXT ",
        initialdir=os.getcwd(),
        filetypes=(("txt files", "*.txt"), ("All files", "*.*")),
    )  # Prompt the user to open a file that contains the Solar Curve txt files, and assign the file path to the variable Solar_TXT
    Solar_Data = txtImp.import_txt(
        Solar_TXT
    )  # Import the Solar curve data into the Solar_Data Variable
    # print(*Solar_Data, sep='\n')                                          # For debugging purposes

    (
        divide_lambda_list,
        Jsc_sum_1,
        Jsc_sum_2,
        Jsc_total,
    ) = EtJ.EQE_vs_div_wavelength_curve(EQE_Data_1, EQE_Data_2, Solar_Data)

    plt.figure()
    plt.plot(divide_lambda_list, Jsc_sum_1, label="EQE 1 Photocurrent")
    plt.plot(divide_lambda_list, Jsc_sum_2, label="EQE 2 Photocurrent")
    plt.plot(divide_lambda_list, Jsc_total, label="Total Photocurrent")
    plt.title("Jsc vs dividing Wavelength for Two EQE curves")
    plt.legend(loc="upper right")
    plt.xlabel("dividing Wavelength /nm")
    plt.ylabel("Jsc / ma / cm^2")

    EQE_Jsc_list_1 = JfE.Jsc_per_nm_list_from_EQE(EQE_Data_1, Solar_Data)
    EQE_Eff_list_1 = JfE.Per_nm_Jsc_to_Per_nm_Eff(EQE_Jsc_list_1, 0.7, 60)

    print(str(Integrated_Jsc(EQE_Jsc_list_1)) + " mA * cm^-2")
    print(str(Integrated_Eff(EQE_Eff_list_1)) + " %")
    # print(*EQE_Eff_list_1,sep='\n')

    plt.figure()
    plt.plot(
        sf.Extract_Column(EQE_Jsc_list_1, 0),
        sf.Extract_Column(EQE_Jsc_list_1, 1),
        label="EQE Photocurrent",
    )
    plt.plot(
        sf.Extract_Column(EQE_Eff_list_1, 0),
        sf.Extract_Column(EQE_Eff_list_1, 1),
        label="EQE Efficiency",
    )
    plt.title("Jsc per nm and efficiency per nanometer curves")
    plt.legend(loc="upper right")
    plt.xlabel("dividing Wavelength /nm")
    plt.ylabel("Jsc / ma / cm^2")

    plt.show()

########################################################---------------------------------------------- Uncomment until here to test the script ---------------------------------------------------############################################################################################
