
# --------------------------- The main function of this script is to generate random EQE curves that are somewhat realistic, and handle them through two classes that hold not only the curve values but are able to calculate the individual EQE parameters and the combined EQE parameters of an EQE pair
# --------------------------- The suggested Import method is the following: import Random_EQE_Generator as REG

import numpy as np                                                                                                  # We first import the necessary libraries and other scripts within the same project
import Small_Functions as sf
import Jsc_From_EQE as JfE
import EQE_To_Jsc_Integrator as EtJ
import Cell_Parameters_From_Eg as CfEg

# This first function generates a random EQE curve that starts at min_x and ends at max_x and whose value can oscillate between max_EQE_value and min_EQE_value. Its bandgap can oscillate between min_Bgap and max_Bgap.
# The basic shape of the EQE starts with a sigmoid at 300 nm and it reaches the starting EQE value which is set to be between the max_EQE_value and the min_EQE_value and then it oscillates as it progresses randomly
# through the spectrum trying to minimize big sudden changes and then when it reaches the bandgap (which has been assigned randomly within the range) it drops suddenly with the shape of another sigmoid
def EQE_Random_curve(growth_scale = 0.7,min_wavelength = 300,max_wavelength = 1100,min_Bgap = 450, max_Bgap = 1000,max_EQE_value = 65, min_EQE_value = 10, Normal_start_EQE_dist = False, Normal_start_EQE_center = 40, Normal_start_EQE_stdv = 20):     # This function does not need any argument but it can accept many, to define the precise limits for the generation of the EQE curves

    # First we generate the linear space that will hold the wavelength_list so that the EQE values have a wavelength reference
    wavelength_list = np.linspace((min_wavelength - 100), (max_wavelength + 100), (max_wavelength + 100) - (min_wavelength - 100) + 1)                          # We generate a linear space that will be offset 100 points to each side and it will be comprised of n values one for each wavelength integer within the range

    # We now set the randomly generated variables that will seed the generation of the actual EQE curve
    Bgap_value = (min_Bgap - max_Bgap) * np.random.random() + max_Bgap                                                                                          # We set the Bgap_value as a completely random value within the specified bandgap range

    # If the user desires a specified EQE range it can be set as an argument and the user can also provide the center of the starting normal distribution and the standard deviation, if not provided the default values will be taken.
    if Normal_start_EQE_dist:
        Initial_EQE = max(min_EQE_value,min(max_EQE_value,np.random.normal(Normal_start_EQE_center,Normal_start_EQE_stdv)))              # We coerce the initial EQE value to the minimum and maximum EQE values

    # Otherwise we use a weighted distribution to promote higher EQE values
    else:
        Seed_for_random_initial_EQE_value = -(np.random.power(5) - 1) + 0.05  # We prepare power shaped random seed so that higher EQE values are slightly favoured against lower ones
        Initial_EQE = (min_EQE_value-max_EQE_value) * Seed_for_random_initial_EQE_value + max_EQE_value                                                             # We then calculate the random Initial_EQE

    # We now prepare the function that will be multiplied to the random values to result in the shape of a more or less realistic EQE curve. It is basically a top hat function that instead of raising sharply it raises and falls with the shape of a sigmoid
    Top_hat_sigmoid = list()                                                                                                                                         # We initialize the list that will contain all the top hat sigmoid values
    sigmoid_expansion_constant_low = 0.1                                                                                                                        # We set the sigmoid width factor of the raising sigmoid (The lower the coefficient the more spread it becomes)
    sigmoid_expansion_constant_high = 0.1                                                                                                                       # We set the sigmoid width factor of the falling sigmoid (The lower the coefficient the more spread it becomes)
    for wavelength in wavelength_list:                                                                                                                          # We loop through the wavelength_list and assign a multiplying factor to each wavelength value according to the two sigmoid functions
        # The sigmoid function is basically composed of two sigmoid functions multiplied, The first one is a sigmoid function that raises from 0 to 1, 50 nm higher than the min_wavelength, and the other sigmoid function falls exactly at the Bgap_value from 1 to 0
        Sigmoid_value = (1 / (1 + np.exp(sigmoid_expansion_constant_high * (-wavelength + min_wavelength + 50))))*(1-(1 / (1 + np.exp(sigmoid_expansion_constant_low * (-wavelength + Bgap_value)))))  # We store the value within a temporal variable
        Top_hat_sigmoid.append(Sigmoid_value)                                                                                                                        # When the value has been calculated we append it to the Bg_sigmoid list for further processing

    # Now we actually generate the random EQE values with all the parameters we have prepared
    escape_constant = 100                                                                                                                                       # We set an escape constant parameter, which is an experimental constant to prevent the EQE value from getting stuck at the max or min values
    Raw_EQE_values = list()                                                                                                                                     # We initialize the list that will contain the EQE curve values
    Current_EQE = Initial_EQE                                                                                                                                   # We set the Current_EQE variable as the Initial_EQE to initialize the calculation at the randomly chosen EQE value
    for wavelength in wavelength_list:                                                                                                                          # Now we loop through all the wavelengths to calculate random EQE values at each wavelength
        Raw_EQE_values.append(Current_EQE)                                                                                                                      # First we append the current result to the EQE_values list before proceeding to the actual calculation. This value will be changed at each iteration
        z = 1 / (1 + np.exp((-Current_EQE + max_EQE_value+10)))                                                                                                 # The z parameter rapidly becomes 1 when the Current_EQE value comes close to the max_EQE_value +10
        v = (-1 / (1 + np.exp((-Current_EQE + min_EQE_value-5)))) + 1                                                                                           # The v parameter rapidly becomes 1 when the Current_EQE value comes close to the min_EQE_value -5

        # This function is composed by 3 main distinct terms: The min prevention term, the max prevention term and the random walker term
        # The min prevention term is a term that quickly moves the Current_EQE value up when its value comes too close to the min_EQE_value
        # The max prevention term is a term that quickly moves the Current_EQE value down when its value comes too close to the max_EQE_value
        # The random walker term basically takes the Current_EQE value and adds a random number with a normal distribution to it, that can be either positive or negative. This term is divided by a control term which basically turns the hole term into a one when the Current_EQE value approaches the maximum or minumum limit
        Current_EQE = (min_EQE_value+escape_constant)*v + (max_EQE_value-escape_constant)*z + ((Current_EQE+np.random.normal(scale=growth_scale)) /(1+Current_EQE*(z+v)))  # The min prevention term + the max prevention term + the random walker term (which includes the control term)

    # Now that we have a set of random EQE values we have to shape them into a realistic EQE curve
    Smooth_EQE_values = sf.smooth(Raw_EQE_values,100)                                                       # We first smooth the values to minimize spikes
    EQE_curve = np.multiply(Top_hat_sigmoid, Smooth_EQE_values)                                             # Now we multiply the Smooth_EQE_values with the Top_hat_sigmoid to shape the EQE_curve
    wavelength_list = wavelength_list[100:((max_wavelength+100)-(min_wavelength-100)-100)]                  # Now we trim the wavelength_list to eliminate the edge effects that the smoothing has had on the Raw_EQE_values
    EQE_curve = EQE_curve[100:((max_wavelength+100)-(min_wavelength-100)-100)]                              # We also trim the EQE_curve to eliminate the edge effects that the smoothing has had on the Raw_EQE_values
    EQE_result = list()
    # Finally we assemble a 2D list that will output the EQE_values as well as their corresponding wavelengths for easier data handling
    for index,wavelength in enumerate(wavelength_list):                                                     # We loop through every wavelength within the wavelength list
        EQE_result.append([wavelength,EQE_curve[index]])                                                    # And for each wavelength we set the EQE_curve[index] value to be a list containing both the wavelength and the EQE value itself
    return EQE_result,Bgap_value                                                                            # Finally we return the EQE_curve and also dhe bandgap of the curve


# This is a class specifically designed to hold the information about Random_generated_EQE_curves. As an input it takes an EQE curve and its band gap as a tuple
# With those parameters it can calculate the estimated Voc, the total efficiency the efficiency per nm and the Jsc per nm. If provided with a solar irradiance spectrum.
class Random_generated_EQE_curves:
    def __init__(self,EQE_curve_with_Bgap,Solar_data,Exciton_binding_energy = 0.3,FF = 65):       # The class takes a tuple containing percentage EQE data and a numerical bandgap value in nm
                                                                                            # It also needs the solar spectrum to calculate the all the per_nm curves
                                                                                            # As a third optional input it accepts the Voc loss constant offset which is the amount of voc loss
                                                                                            # that depends mainly on the cell fabrication quality and varies a lot from cell to cell
        self.EQE_curve, self.Bgap  = EQE_curve_with_Bgap                                    # The values are then split into two different variables, one for the EQE and one for the bandgap value
        self.Eg = (1240/self.Bgap)                                                          # We transform the bgap from nm to eV
        self.FF = FF                                                                        # We initialize the variable that will hold the FF, this is a value which will always be constant and will be used for further calculations
        self.Jsc_per_nm = JfE.Jsc_per_nm_list_from_EQE(self.EQE_curve, Solar_data)          # Afterwards using external functions described in the Jsc_From_EQE script we extract the Jsc_per_nm values
        self.Max_theoretical_Jsc = CfEg.Integrated_Solar_Spectrum_to_Jsc(Solar_data,self.Eg)    # We first calculate the maximum theoretical Jsc that this cell could achieve in order to calculate the Voc
                                                                                            # We also estimate the Voc value from the provided bandgap value with calculations further explained in the Cell parameters from Eg script
        self.Voc = CfEg.Voc_from_Eg(self.Eg,self.Max_theoretical_Jsc) - 0.5*Exciton_binding_energy - CfEg.Non_radiative_Voc_losses(self.Eg)
        self.Voc = (self.Voc if (self.Voc >= 0) else 0)                                     # If the Voc drops below 0 keep it at 0
        self.Eff_per_nm = JfE.Per_nm_Jsc_to_Per_nm_Eff(self.Jsc_per_nm,self.Voc,self.FF)    # We also calculate the Eff_per_nm from the Jsc_per_nm using external functions described in the Jsc_From_EQE script
        self.Total_Eff = EtJ.Integrated_Eff(self.Eff_per_nm)                                # Finally from the Eff_per_nm curve we integrate the Total_Eff
        self.Total_Jsc = EtJ.Integrated_Jsc(self.Jsc_per_nm)                                # Finally from the Jsc_per_nm curve we integrate the Total_Jsc
        self.Name = 'Random Generated EQE curve'                                            # We added a name functionality so that it is compatible with real EQE curve class
        self.Integrated_Jsc_correction_factor = 1                                           # We add a correction factor that will correct the integrated Jsc to be closer to the real Jsc value since on the
                                                                                            # randomly generated EQE curves we do not dispose of JV data, we will leave it as 1 unless we compare random EQE
                                                                                            # data with real data, in which case we will match externally this factor with that of the real EQE data



# This class is specifically designed to hold two randomly generated EQE curves and split the spectrum between the two obtaining efficiency curves for each spectral splitting
# It also calculates meta parameters from the EQE curves like their Efficiency difference, the difference between their overlap, etc.
class Random_generated_EQE_Pair:
    def __init__(self,Random_EQE_1,Random_EQE_2,Solar_data):                        # This class takes two randomly generated EQE curves as its input
        self.Random_EQE_1 = Random_EQE_1                                            # The EQE curves are stored in two separate variables in the shape of a list
        self.Random_EQE_2 = Random_EQE_2
        self.EQE_Overlap = sf.Calc_2_function_overlap_percent(self.Random_EQE_1.EQE_curve, self.Random_EQE_2.EQE_curve)                                         # First we measure the overlap between these two EQE functions. This is accomplished with external functions from the script Small_Functions.py
        self.Efficiency_diff = abs(self.Random_EQE_1.Total_Eff - self.Random_EQE_2.Total_Eff)                                                                   # We also measure the Efficiency difference between the two cells
        self.Jsc_diff = abs(EtJ.Integrated_Jsc(self.Random_EQE_1.Jsc_per_nm) - EtJ.Integrated_Jsc(self.Random_EQE_2.Jsc_per_nm))                                # We calculate the difference in total Jsc between the two EQE curves
        self.Voc_diff = abs(self.Random_EQE_1.Voc - self.Random_EQE_2.Voc)                                                                                      # We also calculate the Voc difference between the two EQE curves
        # Here is where we actually divide the spectrum between the two EQE curves and calculate the resulting Jsc contribution of each cell for each dividing wavelength
        # The function, further described in the EQE_To_Jsc_Integrator script, gives out the Dividing_wavelength_list
        self.Dividing_wavelength_list, self.Jsc_Dividing_wavelength_graph_1,self. Jsc_Dividing_wavelength_graph_2, self.Jsc_Dividing_wavelength_graph_total = EtJ.EQE_vs_div_wavelength_curve(self.Random_EQE_1.EQE_curve,self.Random_EQE_2.EQE_curve,Solar_data)
        # Here we convert the Jsc_per_nm lists that we extracted from the two EQE curves for each dividing wavelength into Eff per nm lists by using the Per_nm_Jsc_to_Eff function further described in the Jsc_From_EQE script
        self.Eff_Dividing_wavelength_graph_1 = JfE.Jsc_list_1D_to_Eff_list_1D(self.Jsc_Dividing_wavelength_graph_1, self.Random_EQE_1.Voc,self.Random_EQE_1.FF)         # We calculate it for the first curve
        self.Eff_Dividing_wavelength_graph_2 = JfE.Jsc_list_1D_to_Eff_list_1D(self.Jsc_Dividing_wavelength_graph_2, self.Random_EQE_2.Voc,self.Random_EQE_2.FF)         # We calculate it for the second curve
        self.Eff_Dividing_wavelength_graph_total = sf.add_two_1D_number_lists(self.Eff_Dividing_wavelength_graph_1, self.Eff_Dividing_wavelength_graph_2)               # We calculate it for the total curve by adding each element of the list with a function from the script Small_Functions
        self.Eff_Enhancement_factor = (max(self.Eff_Dividing_wavelength_graph_total))/(max(self.Random_EQE_1.Total_Eff,self.Random_EQE_2.Total_Eff))                    # We calculate the Efficiency_Enhancement_factor as the relation of the maximum achieved efficiency and the maximum efficiency of the most efficient EQE curve on its own



# --------------------------------------------------------------------------------------------- REG tester program, uncomment if you want to debug this script: ---------------------------------------------------------------------------------------------------
#
import Text_Importer as txtImp
from tkinter import filedialog
import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

if __name__ == '__main__':

    Solar_TXT = filedialog.askopenfilename(title='Select the Solar Curve Spectrum TXT ',initialdir=os.getcwd(), filetypes=(('txt files','*.txt'),('All files','*.*')))   # Prompt the user to open a file that contains the Solar Curve txt files, and assign the file path to the variable Solar_TXT
    Solar_Data = txtImp.import_txt(Solar_TXT)                        # Import the Solar curve data into the Solar_Data Variable


    EQE_0,foo = EQE_Random_curve()                                                          # Random EQE test


    EQE1 = Random_generated_EQE_curves(EQE_Random_curve(Normal_start_EQE_dist= True,Normal_start_EQE_center=30),Solar_Data)                       # Random EQE class test
    EQE2 = Random_generated_EQE_curves(EQE_Random_curve(Normal_start_EQE_dist= True,Normal_start_EQE_center=30),Solar_Data)

    EQE_pair_1 = Random_generated_EQE_Pair(EQE1,EQE2,Solar_Data)                            # Random EQE pair class test


    # Print to test Random EQE generation function
    # print(*EQE_0,sep='\n')


    # Prints for debugging Random EQE class methods
    # print(*EQE2.EQE_curve,sep='\n')
    # print(*EQE2.Eff_per_nm,sep='\n')
    # print(*EQE2.Jsc_per_nm,sep='\n')


    # Prints to test Random EQE class method
    print('Voc = '+str(EQE2.Voc)+ ' V')
    print('Total Efficiency = '+str(EQE2.Total_Eff)+ ' %')


    # Prints to test Random EQE pair class method test
    print('Jsc difference = '+str(EQE_pair_1.Jsc_diff)+ ' mA * cm^-2')
    print('Voc difference = '+str(EQE_pair_1.Voc_diff)+ ' V')
    print('Efficiency difference = '+str(EQE_pair_1.Efficiency_diff)+ ' %')
    print('EQE overlap = '+str(EQE_pair_1.EQE_Overlap)+ ' %')

    # --------------------------------------------------------- Plot Section ------------------------------------------------------------------

    plt.figure()                                                                                    # Plot one of the random generated curves
    plt.plot(sf.Extract_Column(EQE_0,0),sf.Extract_Column(EQE_0,1), label = 'EQE 1')
    plt.title('Random EQE Curves')
    plt.legend(loc='upper right')
    plt.xlabel('Wavelength /nm')
    plt.ylabel('EQE /%')

    plt.figure()                                                                                    # Plot one of the random generated curves extracted from a class
    plt.plot(sf.Extract_Column(EQE2.EQE_curve,0),sf.Extract_Column(EQE2.EQE_curve,1), label = 'EQE 2')
    plt.plot(sf.Extract_Column(EQE1.EQE_curve, 0), sf.Extract_Column(EQE1.EQE_curve, 1), label='EQE 1')
    plt.title('Random EQE Extracted from the class')
    plt.legend(loc='upper right')
    plt.xlabel('Wavelength /nm')
    plt.ylabel('EQE /%')

    plt.figure()                                                                                    # Plot one of the random generated curves Eff_per_nm extracted from a class
    plt.plot(sf.Extract_Column(EQE2.Eff_per_nm,0),sf.Extract_Column(EQE2.Eff_per_nm,1), label = 'EQE 1')
    plt.title('Random EQE Efficiency per nm')
    plt.legend(loc='upper right')
    plt.xlabel('Wavelength /nm')
    plt.ylabel('EQE /%')

    plt.figure()                                                                                    # Plot one of the random generated curves Jsc_per_nm extracted from a class
    plt.plot(sf.Extract_Column(EQE2.Jsc_per_nm,0),sf.Extract_Column(EQE2.Jsc_per_nm,1), label = 'EQE 1')
    plt.title('Random EQE Jsc per nm')
    plt.legend(loc='upper right')
    plt.xlabel('Wavelength /nm')
    plt.ylabel('Jsc / ma * cm^-2 * nm')


    # In this section we plot the efficiency and the jsc vs the dividing wavelength and we also plot both EQE curves to see their shape and which perform the best

    # Create 2x2 sub plots and then span the third graph onto the lower two subplots
    gs = gridspec.GridSpec(2, 2)

    fig = plt.figure(figsize=(13, 13))                                                                                          # We set a big figure size so that we can actually see what is going on
    fig.suptitle('Two Random EQE generated curves compared', fontsize=16)
    ax1 = fig.add_subplot(gs[0, 0]) # row 0, col 0
    ax1.plot(EQE_pair_1.Dividing_wavelength_list,EQE_pair_1.Eff_Dividing_wavelength_graph_1, label = 'EQE 1 Efficiency')        # The first figure is the efficiency vs the dividing wavelength
    ax1.plot(EQE_pair_1.Dividing_wavelength_list,EQE_pair_1.Eff_Dividing_wavelength_graph_2, label = 'EQE 2 Efficiency')
    ax1.plot(EQE_pair_1.Dividing_wavelength_list,EQE_pair_1.Eff_Dividing_wavelength_graph_total, label = 'Total Efficiency')
    ax1.set_title('Efficiency vs Dividing Wavelength')
    ax1.legend(loc='upper right')
    ax1.set(xlabel= 'Dividing Wavelength /nm',ylabel ='Efficiency /%' )

    ax2 = fig.add_subplot(gs[0, 1]) # row 0, col 1
    ax2.plot(EQE_pair_1.Dividing_wavelength_list,EQE_pair_1.Eff_Dividing_wavelength_graph_1, label = 'EQE 1 Jsc')               # The second thing we plot is the Jsc vs Dividing wavelength
    ax2.plot(EQE_pair_1.Dividing_wavelength_list,EQE_pair_1.Eff_Dividing_wavelength_graph_2, label = 'EQE 2 Jsc')
    ax2.plot(EQE_pair_1.Dividing_wavelength_list,EQE_pair_1.Eff_Dividing_wavelength_graph_total, label = 'Total Jsc')
    ax2.set_title('Jsc vs Dividing Wavelength')
    ax2.legend(loc='upper right')
    ax2.set(xlabel= 'Dividing Wavelength /nm',ylabel ='Jsc / mA * cm^-2' )

    ax3 = fig.add_subplot(gs[1, :]) # row 1, span all columns
    ax3.plot(sf.Extract_Column(EQE1.EQE_curve,0),sf.Extract_Column(EQE1.EQE_curve,1), label = 'EQE Curve 1')                                    # The third thing we plot are the actual EQE curves
    ax3.plot(sf.Extract_Column(EQE2.EQE_curve,0),sf.Extract_Column(EQE2.EQE_curve,1), label = 'EQE Curve 2')
    ax3.set_title('EQE values')
    ax3.legend(loc='upper right')
    ax3.set(xlabel= 'Wavelength /nm',ylabel ='EQE /%' )

    plt.show()
#

########################################################---------------------------------------------- Uncomment until here to test the script ---------------------------------------------------############################################################################################