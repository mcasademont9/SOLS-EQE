import Text_Importer as txtImp
from tkinter import filedialog
import os
import Small_Functions as sf
import matplotlib.pyplot as plt
import Random_EQE_Generator as REG
import matplotlib.gridspec as gridspec

Solar_TXT = filedialog.askopenfilename(title='Select the Solar Curve Spectrum TXT ',initialdir=os.getcwd(), filetypes=(('txt files','*.txt'),('All files','*.*')))   # Prompt the user to open a file that contains the Solar Curve txt files, and assign the file path to the variable Solar_TXT
Solar_Data = txtImp.import_txt(Solar_TXT)                        # Import the Solar curve data into the Solar_Data Variable


EQE_0,foo = REG.EQE_Random_curve()                                                          # Random EQE test


EQE1 = REG.Random_generated_EQE_curves(REG.EQE_Random_curve())                              # Random EQE class test
EQE2 = REG.Random_generated_EQE_curves(REG.EQE_Random_curve())

EQE1.update_parameters(Solar_Data)                                                          # Random EQE class methods test
EQE2.update_parameters(Solar_Data)

EQE_pair_1 = REG.Random_generated_EQE_Pair(EQE1,EQE2)                                       # Random EQE pair class test

EQE_pair_1.Update_pair_parameters(Solar_Data)                                               # Random EQE pair class method test


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
plt.title('Random EQE Curve')
plt.legend(loc='upper right')
plt.xlabel('Wavelength /nm')
plt.ylabel('EQE /%')

plt.figure()                                                                                    # Plot one of the random generated curves extracted from a class
plt.plot(sf.Extract_Column(EQE2.EQE_curve,0),sf.Extract_Column(EQE2.EQE_curve,1), label = 'EQE 1')
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
ax3.plot([0,1])
ax3.plot(sf.Extract_Column(EQE1.EQE_curve,0),sf.Extract_Column(EQE1.EQE_curve,1), label = 'EQE 1 Jsc')                                    # The third thing we plot are the actual EQE curves
ax3.plot(sf.Extract_Column(EQE2.EQE_curve,0),sf.Extract_Column(EQE2.EQE_curve,1), label = 'EQE 2 Jsc')
ax3.set_title('EQE values')
ax3.legend(loc='upper right')
ax3.set(xlabel= 'Wavelength /nm',ylabel ='EQE /%' )

plt.show()