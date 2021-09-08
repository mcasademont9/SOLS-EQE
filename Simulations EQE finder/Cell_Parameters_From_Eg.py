
# ---------------------------------------------------- This scripts main function is to calculate the theoretical maximum performance of solar cells according to their Band gap energy.
# ---------------------------------------------------- The suggested import method is the following: import import Cell_Parameters_From_Eg as CfEg


from scipy import integrate                                                 # First we import the necessary libraries and scripts
import List_Finder as lstf

# This function calculates the diode reverse saturation current according to the Shockley Queisser equations
def Saturation_Current_Calculation(Eg_eV,T = 300):                          # This function accepts 2 inputs. The first and required one is the band gap energy (or the charge transfer energy in the case of organics)
                                                                            # The second one is the temperature which is set as a default on 300K
    q = 1.602176634 * 10 ** (-19)  # C                                      # We have to define the universal constants
    k = 1.38064852 * 10 ** (-23)  # m2 kg s-2 K-1
    sigma = 5.670374419 * 10 ** (-8)  # W⋅m−2⋅K−4

    u = (Eg_eV * q) / (k * T)                                               # We also define this term which will make the integration process easier

    # In order to calculate the J0 more easily, we divide it into two terms
    J0_constant = (q * 15 * sigma * T ** 3) / (k * np.pi ** 4)              # The first one is the constant term

    integral_term_expression = lambda x: (x ** 2) / (np.exp(x) - 1)         # We have to predefine the function to be integrated
    integral_term = integrate.quad(integral_term_expression, u, np.inf)     # And the second one is the integral term

    J0 = J0_constant * integral_term[0]                                     # And finally to calculate the J0 we multiply the two terms and return J0 as the result

    return J0

# This function returns the theoretical maximum Jsc value for a given Eg and given EQE
def Integrated_Solar_Spectrum_to_Jsc(Solar_Data,Eg_eV,Irradiance_Column = 1,EQE=1):                 # This function takes the solar spectrum data in the shape of a 2d list, the band gap energy in eV, the column where the irradiance is located within the solar data and the EQE value.

    Bgap_Lambda = 1240/Eg_eV                                                                        # We first convert the Eg into nm for the following calculations
    Bgap_Lambda_index = lstf.find_closest(Bgap_Lambda,Solar_Data,max_tolerance=10)                  # We find the closest value on the solar spectrum and return the index
    Jsc = 0                                                                                         # We initialize the Jsc value
    Previous_Lambda = Solar_Data[0][0] - (Solar_Data[1][0] - Solar_Data[0][0])                      # We define the Previous labda to be one lambda differential before the first lambda so that we do not lose any integration step

    # Now we loop through the solar spectrum adding the individual Jsc contributions until we reach the Bgap wavelength that we found earlier
    for i in range(Bgap_Lambda_index):
        Current_Lambda = Solar_Data[i][0]                                                           # We extract the current wavelength
        Lambda_differential = Current_Lambda - Previous_Lambda                                      # We define the lambda differential used on the integration
        Current_Irradiance = Solar_Data[i][Irradiance_Column]                                       # We extract the irradiance at the current wavelength
        Temp_Jsc = (EQE*Lambda_differential*Current_Irradiance*Current_Lambda/1240)                 # We calculate the current wavelength's contribution to the total Jsc
        Jsc = Jsc + Temp_Jsc                                                                        # We add the current wavelength's contribution to the total Jsc
        Previous_Lambda = Current_Lambda                                                            # We redefine the previous lambda with the current lambda so that in the next loop it will be taken into consideration

    return Jsc                                                                                      # Finally we return the total Jsc contribution


# This function calculates the theoretical maximum Voc value according to the Shockley Queisser limit for a given Band gap energy (or charge transfer energy in the case of organics)
def Voc_from_Eg(Eg_eV,max_Jsc,n=1,T=300):                                                           # This function takes as an Input the Eg in eV, the maximum Jsc at that exact Bgap, the ideality factor of the diode, which is set by default at 1, and the temperature which is set to 300 K
    q = 1.602176634 * 10 ** (-19)  # C                                                              # We have to define the universal constants
    k = 1.38064852 * 10 ** (-23)  # m2 kg s-2 K-1

    J0 = Saturation_Current_Calculation(Eg_eV,T)                                                    # We first calculate the reverse saturation current with one of the functions described above
    Voc = ((n * k * T) / q) * np.log((max_Jsc / J0) + 1)                                            # And finally we calculate the Voc with all the previously derived parameters according to the diode equation

    return Voc                                                                                      # And we return the Voc value

# This function calculates the maximum theoretical PCE according to the diode equation for a given Band gap energy
def PCE_from_Eg(Voc,Jsc,J0,n=1,T=300):
    q = 1.602176634 * 10 ** (-19)  # C                                      # We have to define the universal constants
    k = 1.38064852 * 10 ** (-23)  # m2 kg s-2 K-1

    V = np.arange(0, Voc, 0.001)                                            # We define an array from 0 to Voc to find the Vmpp and the Jmpp points
    J = -1 * Jsc + J0 * (np.exp(q * V / (n * k * T)) - 1)                   # Now we calculate the Current according to the diode equation at each point
    PCE = (-100 * np.min(J * V)/1000)                                       # The PCE will be the minimum value of the product between J and V divided by the sun intensity (1000 W / m^2 ). We change its sign to have a positive PCE and multiply it by 100 to have it in percentual form

    return PCE                                                              # Finally we return the PCE value

# This function calculates the non radiative losses for a certain Eg value according to Koen Vandewal's paper: https://doi.org/10.1038/s41563-019-0324-5
def Non_radiative_Voc_losses(Eg_ev):                                        # As an input we just need the energy of the Band gap
    Voc_loss = ((30*Eg_ev**2) - (352*Eg_ev) + 815)/1000                     # To calculate the losses we have fitted Koen's data with a polynomial fit so that it is easier to calculate (we divide over 1000 to convert from mV to V)
    return Voc_loss                                                         # Finally we return the Voc loss value due to non radiative recombination

# ----------------------------------------------------------------------------------------- CfEg tester program, uncomment if you want to debug this script: ---------------------------------------------------------------------------------------------------

import numpy as np
from scipy import integrate
import Text_Importer as txtImp
from tkinter import filedialog
import matplotlib.pyplot as plt
import Small_Functions as sf
import List_Finder as lstf
import matplotlib.gridspec as gridspec

if __name__=='__main__':

    Compare_Koen = True

    Solar_Data = txtImp.import_txt(filedialog.askopenfilename(title='Select the Solar Curve Spectrum file ', initialdir=r'C:\Users\minus\Documents\PhD\Rainbow\Curve data From enrique EQE',
                                                              filetypes=(('txt files', '*.txt'), ('All files', '*.*'))))  # Prompt the user to open a file that contains the Solar Curve txt files, and import it as a txt file into the Solar_Data variable

    # If we want to compare our results with those of Koen vandewal we will ask for his data
    if Compare_Koen:
        Koen_Voc_ShkQss = txtImp.import_txt(filedialog.askopenfilename(title='Select the Koen Shockley Queisser limit Voc file ', initialdir=r'C:\Users\minus\Documents\PhD\Rainbow\Curve data From enrique EQE',
                                                              filetypes=(('txt files', '*.txt'), ('All files', '*.*'))))  # Prompt the user to open a file that contains the Solar Curve txt files, and import it as a txt file into the Solar_Data variable

    Jsc_list = list()                                       # We define lists that will hold the values at each Eg value of each parameter
    Voc_list = list()
    PCE_list = list()
    J0_list = list()

    for index,Solar_Data_Row in enumerate(Solar_Data):  # For loop that iterates through every element within the EQE_Data list
        # We only operate after the first cycle to prevent the condition in which the PCE is 0 due to the Voc and the Jsc being both 0
        if index > 0:
            Current_Lambda = Solar_Data_Row[0]                          # We set the Current_Lambda variable with the value of lambda extracted from the current row
            Current_Eg = 1240/Current_Lambda                            # We transform the Current lambda into eV

            # We calculate each cell parameter for the current Eg value
            J0_Temp = Saturation_Current_Calculation(Current_Eg)
            Jsc_Temp = Integrated_Solar_Spectrum_to_Jsc(Solar_Data,Current_Eg,Irradiance_Column=3)
            Voc_Temp = Voc_from_Eg(Current_Eg,Jsc_Temp)
            PCE_Temp = PCE_from_Eg(Voc_Temp,Jsc_Temp,J0_Temp)

            # We append them into their corresponding lists
            J0_list.append([Current_Lambda, J0_Temp,Current_Eg])
            Jsc_list.append([Current_Lambda, Jsc_Temp,Current_Eg])
            Voc_list.append([Current_Lambda, Voc_Temp,Current_Eg])
            PCE_list.append([Current_Lambda, PCE_Temp,Current_Eg])

    # Finally we plot the results on a graph

    gs = gridspec.GridSpec(2, 2)  # Create 2x2 sub plots

    fig = plt.figure(figsize=(12, 9))  # We set a big figure size so that we can actually see what is going on
    fig.suptitle('Shockley Queisser limits on solar cell parameters', fontsize=16)

    ax1 = fig.add_subplot(gs[0, 0])  # row 0, col 0
    ax1.plot(sf.Extract_Column(J0_list,2),sf.Extract_Column(J0_list,1))
    ax1.set_title('Reverse Saturation Current Density vs Band gap Energy')
    ax1.set(xlabel='Band Gap Energy /eV', ylabel='Reverse Saturation Current Density /A * m^-2')
    ax1.set_yscale('log')

    ax2 = fig.add_subplot(gs[0, 1])  # row 0, col 0
    ax2.plot(sf.Extract_Column(Jsc_list,2),sf.Extract_Column(Jsc_list,1))
    ax2.set_title('Short Circuit Current Density vs Band gap Energy')
    ax2.set(xlabel='Band Gap Energy /eV', ylabel='Short Circuit Current Density /A * m^-2')

    ax3 = fig.add_subplot(gs[1, 0])  # row 0, col 0
    ax3.plot(sf.Extract_Column(Voc_list,2),sf.Extract_Column(Voc_list,1),label='Our Voc Calculation')
    if Compare_Koen:
        ax3.plot(sf.Extract_Column(Koen_Voc_ShkQss,0),sf.Extract_Column(Koen_Voc_ShkQss,1),label='Koen Voc calculation')
        ax3.legend(loc='lower right')
    ax3.set_title('Open Circuit Voltage vs Band gap Energy')
    ax3.set(xlabel='Band Gap Energy /eV', ylabel='Open Circuit Voltage /V')

    ax4 = fig.add_subplot(gs[1, 1])  # row 0, col 0
    ax4.plot(sf.Extract_Column(PCE_list,2),sf.Extract_Column(PCE_list,1))
    ax4.set_title('Power Conversion Efficiency vs Band gap Energy')
    ax4.set(xlabel='Band Gap Energy /eV', ylabel='Power Conversion Efficiency /%')

    plt.subplots_adjust(hspace=0.3,wspace=0.3)

    plt.show()

########################################################---------------------------------------------- Uncomment until here to test the script ---------------------------------------------------############################################################################################


