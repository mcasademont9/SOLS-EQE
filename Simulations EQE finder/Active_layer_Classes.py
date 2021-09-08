
# -------------------------------------------------------- This script main function is to define the classes that will hold the EQE and Jv curve information for each material and which will also calculate the efficiency of each solar cell for all possible spectral divisions
# -------------------------------------------------------- The recommended import method for this script is the following: import Active_layer_Classes as AlC

import JV_Parameters_From_JV_Curve as JV_Par                                                    # First we import all the necessary scripts that we will need
import EQE_To_Jsc_Integrator as EtJ
import Jsc_From_EQE as JfE
import Small_Functions as sf
from statistics import mean
import Bgap_Finder as BgF


# This is a class specifically designed to hold the EQE and JV curve information for each and every Active layer material. As an input it takes an EQE curve and a JV curve
# With those parameters it can calculate the Voc, the Jsc and the FF of the cell.
class Active_layer:
    def __init__(self, Name, JV_curve, EQE_curve,Solar_data):                                   # The class takes a tuple containing the material name, a JV curve list, a percentual EQE data and a list containing the solar irradiance spectrum
        self.Name = Name                                                                        # We then store all the values within the class variables
        self.JV_curve = JV_curve
        self.EQE_curve = EQE_curve
        self.Jsc, self.Voc, self.FF = JV_Par.JV_Par_from_JV_curv(self.JV_curve)                 # We also calculate the Jsc, Voc and FF from the provided JV curve
        self.Jsc_per_nm = JfE.Jsc_per_nm_list_from_EQE(self.EQE_curve, Solar_data)              # Afterwards using external functions described in the Jsc_From_EQE script we extract the Jsc_per_nm values
        self.Eff_per_nm = JfE.Per_nm_Jsc_to_Per_nm_Eff(self.Jsc_per_nm, self.Voc, self.FF)      # We also calculate the Eff_per_nm from the Jsc_per_nm using external functions described in the Jsc_From_EQE script
        self.Total_Eff = EtJ.Integrated_Eff(self.Eff_per_nm)                                    # Finally from the Eff_per_nm curve we integrate the Total_Eff
        self.Total_Jsc = EtJ.Integrated_Jsc(self.Jsc_per_nm)                                    # Finally from the Jsc_per_nm curve we integrate the Total_Jsc
        self.Integrated_Jsc_correction_factor = self.Jsc/self.Total_Jsc                         # We add a correction factor that will correct the integrated Jsc to be closer to the real Jsc value



# This class is specifically designed to hold two Active_layer material information classes and split the spectrum between the two obtaining efficiency curves for each spectral splitting
class Active_layer_Pair:
    def __init__(self, Active_layer_1, Active_layer_2,Solar_data):                                                      # This class takes two Active_layer material information classes and a solar irradiance spectrum
        self.Full_Name = Active_layer_1.Name + '-' + Active_layer_2.Name                                      # We store the full Active Layer pair name as a variable
        self.Name_1st = Active_layer_1.Name
        self.Name_2nd = Active_layer_2.Name
        self.Active_layer_1 = Active_layer_1                                                                    # We also store the layer classes for convenience
        self.Active_layer_2 = Active_layer_2
        self.Solar_spectrum = Solar_data
        # Here is where we actually divide the spectrum between the two EQE curves and calculate the resulting Jsc contribution of each cell for each dividing wavelength
        # The function, further described in the EQE_To_Jsc_Integrator script, gives out the Dividing_wavelength_list
        self.Dividing_wavelength_list, self.Jsc_Dividing_wavelength_graph_1,self. Jsc_Dividing_wavelength_graph_2, self.Jsc_Dividing_wavelength_graph_total = EtJ.EQE_vs_div_wavelength_curve(Active_layer_1.EQE_curve,Active_layer_2.EQE_curve,Solar_data,Active_layer_1.Integrated_Jsc_correction_factor,Active_layer_2.Integrated_Jsc_correction_factor)
        # Here we convert the Jsc_per_nm lists that we extracted from the two EQE curves for each dividing wavelength into Eff per nm lists by using the Per_nm_Jsc_to_Eff function further described in the Jsc_From_EQE script
        self.Eff_Dividing_wavelength_graph_1 = JfE.Jsc_list_1D_to_Eff_list_1D(self.Jsc_Dividing_wavelength_graph_1, Active_layer_1.Voc,Active_layer_1.FF)         # We calculate it for the first curve
        self.Eff_Dividing_wavelength_graph_2 = JfE.Jsc_list_1D_to_Eff_list_1D(self.Jsc_Dividing_wavelength_graph_2, Active_layer_2.Voc,Active_layer_2.FF)         # We calculate it for the second curve
        self.Eff_Dividing_wavelength_graph_total = sf.add_two_1D_number_lists(self.Eff_Dividing_wavelength_graph_1, self.Eff_Dividing_wavelength_graph_2)         # We calculate it for the total curve by adding each element of the list with a function from the script Small_Functions
        self.Eff_Enhancement_factor = (max(self.Eff_Dividing_wavelength_graph_total))/(max(mean(self.Eff_Dividing_wavelength_graph_total[0:10]),mean(self.Eff_Dividing_wavelength_graph_total[-10:-1])))          # We calculate the Efficiency_Enhancement_factor as the relation of the maximum achieved efficiency and the maximum efficiency of the most efficient EQE curve on its own

# --------------------------------------------------------------------------------------------- AlC tester program, uncomment if you want to debug this script: ---------------------------------------------------------------------------------------------------
#
import Text_Importer as txtImp                                              # We import the necessary libraries and other scripts from the same project
from tkinter import filedialog
import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

if __name__ == '__main__':

    # First we prompt the user to locate the file directory where all the JV and EQE files are located. Note that they must be named with a given convention. Material names for JV curve and EQE curve of the same material must be identical and the only difference
    # between these two files is that one must end with a _JV string and the other with an _EQE string.
    File_Directory = filedialog.askdirectory(title='Select the directory with the EQE curves, Jv curves and solar data files', initialdir=os.getcwd(), mustexist=True)  # Ask for the directory where all the EQE and JV curve files are
    Available_files = os.listdir(File_Directory)                                                                                                                        # Save the available files within a list
    # print(*Available_files,sep='\n')                                                              # Print the available filenames for debugging purposes

    # We create a directory within the folder that has the curves where the figures will be saved
    Save_Directory = sf.Full_path_adder('Binary comparison figures', File_Directory)
    if not os.path.exists(Save_Directory):
        os.mkdir(Save_Directory)

    Active_layers = list()                                                                          # We initialize a list that will hold all the Active_layer classes

    # First we search for the solar irradiance spectrum file:
    Solar_data_found = False                                                                        # We set a flag so that if we do not find the solar data file we stop the whole process and raise an error
    for file in Available_files:
        # We loop through the files searching for the solar data file and save its data within the Solar_Data variable
        # The solar data file has to have the word Solar with the first letter capitalized to be acceptable
        if 'Solar' in file:                                                               # if the current file contains the word solar , we store the solar data it contains in the variable solar data
            Solar_Data = txtImp.import_txt(sf.Full_path_adder(file,File_Directory))         # We store the imported solar data on the Solar_Data variable
            Solar_data_found = True

    # If the solar data has not been found we raise an error
    if not Solar_data_found:
        raise Exception('The solar data has not been found, aborting process')


    # Here we loop through all the available files searching for the files that contain the substrings we are searching for. In this case we are searching for _JV and _EQE
    # The files have to end in _JV or in _EQE to be acceptable and if they are the same active layer material they should have exactly the same name except on the _JV or _EQE ending
    # IMPORTANT WARNING!!!! All materials that want to be processed need both a JV curve and an EQE file, otherwise they will be discarded
    for JV_file in Available_files:                                                            # We first loop through the available files in search for the JV_files
        if '_JV' in JV_file:                                                                        # If the file has the string _JV within its name it means it is a JV curve
            Material_name = JV_file.split('_JV', 1)[0]                                              # We extract the material_name by splitting the filename string and extracting the first column from the resulting list

            for EQE_file in Available_files:                                                        # Now we loop again through the files in search for its EQE file equivalent

                # if the file has the substring _EQE and the material name within the filename it means it's a match and we proceed to extract the data from both files
                if '_EQE' in EQE_file and Material_name in EQE_file:

                    # We extract the EQE curve values and the JV curve values and we store then in an Active_layer class that will be appended to the Active_layers list
                    EQE_curve = txtImp.import_txt(sf.Full_path_adder(EQE_file,File_Directory))      # We, momentarily, store the EQE_curve imported values within the EQE_curve variable
                    JV_curve = txtImp.import_txt(sf.Full_path_adder(JV_file, File_Directory))       # We, momentarily, store the JV_curve imported values within the JV_curve variable
                    Active_layers.append(Active_layer(Material_name, JV_curve, EQE_curve,Solar_Data))          # We append the Active_layer class with the current EQE_curve and JV_curve information as well as the material name within the Active_layers list


    Material_pairs = [[None for y in range(len(Active_layers))] for x in range(len(Active_layers))]         # We now create a 2D list that will hold the Active_layer_pair classes for each Active_layer material combination possible
    Total_figures = len(Active_layers)*len(Active_layers)-len(Active_layers)                                # We calculate the total number of figures that will be generated
    Saved_figures = 0                                                                                       # We also initialize a counter to keep track of the progress
    Timer_1 = sf.Timer()                                                                         # And finally we start a timer that will tell us the approximate time estimate and completion percentage

    for index_1, Active_layer_1 in enumerate(Active_layers):                                                # We loop through each available material
        for index_2, Active_layer_2 in enumerate(Active_layers):                                            # And for each available material we loop again comparing it to all the other available materials
            if index_1 == index_2:                                                                          # If the indexes are the same it means they are the same active material combination so we 'pass' and do not compare them
                pass
            else:                                                                                           # If, otherwise the two indices are not the same we proceed to compare them and plot them
                Material_pairs[index_1][index_2] = Active_layer_Pair(Active_layer_1,Active_layer_2,Solar_Data)      # We store the current material combination within the Material_pairs list as n Active_layer_pair class with the active layers to compare as attributes, and of course the solar data

                # This part is only dedicated to plotting the compared EQE_curves
                gs = gridspec.GridSpec(2, 2)  # Create 2x2 sub plots and then span the third graph onto the lower two subplots

                # In the first subplot we plot the Efficiency vs Dividing wavelength for the current Material_pair

                fig = plt.figure(figsize=(12, 9))  # We set a big figure size so that we can actually see what is going on
                fig.suptitle('Full rainbow analysis for ' + str(Material_pairs[index_1][index_2].Full_Name), fontsize=16)
                ax1 = fig.add_subplot(gs[0, 0])  # row 0, col 0
                ax1.plot(Material_pairs[index_1][index_2].Dividing_wavelength_list, Material_pairs[index_1][index_2].Eff_Dividing_wavelength_graph_1, label=str(Material_pairs[index_1][index_2].Name_1st) + ' Efficiency')  # The first figure is the efficiency vs the dividing wavelength
                ax1.plot(Material_pairs[index_1][index_2].Dividing_wavelength_list, Material_pairs[index_1][index_2].Eff_Dividing_wavelength_graph_2, label=str(Material_pairs[index_1][index_2].Name_2nd) + ' Efficiency')
                ax1.plot(Material_pairs[index_1][index_2].Dividing_wavelength_list, Material_pairs[index_1][index_2].Eff_Dividing_wavelength_graph_total, label='Total Efficiency')
                ax1.set_title('Efficiency vs Dividing Wavelength')
                ax1.legend(loc='center right')
                ax1.set(xlabel='Dividing Wavelength /nm', ylabel='Efficiency /%')

                # In the second subplot we plot the Jsc vs Dividing wavelength for the current Material_pair
                ax2 = fig.add_subplot(gs[0, 1])  # row 0, col 1
                ax2.plot(Material_pairs[index_1][index_2].Dividing_wavelength_list, Material_pairs[index_1][index_2].Jsc_Dividing_wavelength_graph_1, label=str(Material_pairs[index_1][index_2].Name_1st) + ' Photocurrent')  # The second thing we plot is the Jsc vs Dividing wavelength
                ax2.plot(Material_pairs[index_1][index_2].Dividing_wavelength_list, Material_pairs[index_1][index_2].Jsc_Dividing_wavelength_graph_2, label=str(Material_pairs[index_1][index_2].Name_2nd) + ' Photocurrent')
                ax2.plot(Material_pairs[index_1][index_2].Dividing_wavelength_list, Material_pairs[index_1][index_2].Jsc_Dividing_wavelength_graph_total, label='Total Photocurrent')
                ax2.set_title('Jsc vs Dividing Wavelength')
                ax2.legend(loc='center right')
                ax2.set(xlabel='Dividing Wavelength /nm', ylabel='Jsc / mA * cm^-2')

                # In the third subplot we plot the EQE curves so that we can compare them when analyzing the data
                ax3 = fig.add_subplot(gs[1, :])  # row 1, span all columns
                ax3.plot(sf.Extract_Column(Active_layer_1.EQE_curve, 0), sf.Extract_Column(Active_layer_1.EQE_curve, 1), label=Active_layer_1.Name)  # The third thing we plot are the actual EQE curves
                ax3.plot(sf.Extract_Column(Active_layer_2.EQE_curve, 0), sf.Extract_Column(Active_layer_2.EQE_curve, 1), label=Active_layer_2.Name)
                ax3.set_title('EQE curves')
                ax3.legend(loc='upper right')
                ax3.set(xlabel='Wavelength /nm', ylabel='EQE /%')


                # Finally we set the figure name with the directory we want to save it to and we save and close all the figures open to continue through the loop
                fig_name = str(Material_pairs[index_1][index_2].Full_Name).replace(':', '_') + ' Binary rainbow curve.png'
                fig_name = sf.Full_path_adder(fig_name,Save_Directory)
                # print(fig_name)
                plt.savefig(fig_name)
                plt.close('all')

                # We also want to keep the user informed about the progress of the file conversion so we update the timer at every loop and print an informative message
                Saved_figures +=1                                                               # We update the counter every time we save a figure

                Timer_1.Update_progress(Saved_figures,Total_figures,True,True)                            # And we also update the progress value

                # Finally we print an informative message for the user informing about the progress of the calculation
#

########################################################---------------------------------------------- Uncomment until here to test the script ---------------------------------------------------############################################################################################

