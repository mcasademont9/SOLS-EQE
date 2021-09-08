
# ------------------------------------------------- The main goal of this script is to take any EQE spectrum either real or simulated and calculate its optimal rainbow binary partner with highest efficiency enhancement factor
# ------------------------------------------------- To do so it takes a given EQE spectrum and generates as many random EQE spectra as specified and it returns only the specified number of best performing pairs in the form of a single graph, the number of specified graphs and an animation with all matches

# First we import the necessary libraries and functions from other scripts within this project
import Small_Functions as sf
import Random_EQE_Generator as REG
from tkinter import filedialog
import os
import Text_Importer as txtImp
import Active_layer_Classes as AlC
import operator
import matplotlib.pyplot as plt
import matplotlib.pylab as pl
import matplotlib.gridspec as gridspec
import numpy as np
import time


if __name__ == '__main__':

    # First we set the parameters for the scrpit to specify the operations we will want to perform
    Is_spectrum_real = True                                                                             # Do we need to import a real spectrum or will it be generated randomly?
    Match_Multiple_Spectra = True                                                                       # Do we want to match multiple spectra. If True we will have to follow the naming instructions defined in the Match_Multi_Spectra section
    Save_Graphs = True                                                                                 # Will we want to save the generated graphs or we just want to see them?
    Save_Animation = False                                                                               # Will we want to save the animation for each of the best performing cell pairs?
    Save_Animation_Individual_graphs = False                                                             # Do we want to save each of the best performing cell pairs separately as an image? This will only be enabled if the previous variable is TRUE

    Debugging = False                                                                                    # We set a debugging setting to check on the generated random EQE curves and their comparison

    # Now we need to specify the parameters that will determine the match calculations and plotting of the results:
    top_spectra_number = 10                                                                          # 10   # How many top performing spectra will we show in the final graphs
    minimum_suitable_spectra = 200                                                               # 200  # We set the number of minimum suitable spectra that will be used to extract the top ten spectra, the higher this number is the more it will take the calculation to find the best spectra for the main spectrum
    min_enhancement_factor = 1.2                                                                     # 1.2  # What is the minimum enhancement factor to be regarded as a good match
    Main_spectrum_blue_cell = False                                                         # This sets the main spectrum as the one who receives the higher energy part of the spectrum upon dividing it, if set to false it will set it as the spectrum that receives the low part of the spectrum

    # We also need to specify plotting variables
    animation_duration = 20
    frame_duration = animation_duration / top_spectra_number

    # If we want to match a real spectrum we will have to provide a JV curve and an EQE curve to have all the needed factors for the computation
    if Is_spectrum_real:

        # If we want to Match multiple spectra we will have to provide a location where all the JV curve files and the EQE files will be allocated. The naming convention is MATERIALNAME_JV.txt for JV curve files and MATERIALNAME_EQE.txt for EQE files. The material name must
        # be exactly equal on both files otherwise it will not be analyzed. Also no two equal materialnames must exist for different JV or EQE files, this would lead to confusion within the program. If multiple instances of the same material occur
        # a number or brief comment can be added before the _JV or _EQE extension to prevent errors.
        if Match_Multiple_Spectra:
            # First we prompt the user to locate the file directory where all the JV and EQE files are located. Note that they must be named with a given convention. Material names for JV curve and EQE curve of the same material must be identical and the only difference
            # between these two files is that one must end with a _JV string and the other with an _EQE string.
            File_Directory = filedialog.askdirectory(title='Select the directory with the EQE curves, Jv curves and solar data files', initialdir=os.getcwd(), mustexist=True)  # Ask for the directory where all the EQE and JV curve files are
            Available_files = os.listdir(File_Directory)                                                                                                                        # Save the available files within a list
            # print(*Available_files,sep='\n')                                                              # Print the available filenames for debugging purposes



            Active_layers = list()                                                                          # We initialize a list that will hold all the Active_layer classes

            # First we search for the solar irradiance spectrum file:
            Solar_data_found = False  # We set a flag so that if we do not find the solar data file we stop the whole process and raise an error
            for file in Available_files:
                # We loop through the files searching for the solar data file and save its data within the Solar_Data variable
                # The solar data file has to have the word Solar with the first letter capitalized to be acceptable
                if 'Solar' in file:  # if the current file contains the word solar , we store the solar data it contains in the variable solar data
                    Solar_Data = txtImp.import_txt(sf.Full_path_adder(file, File_Directory))  # We store the imported solar data on the Solar_Data variable
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
                            Active_layers.append(AlC.Active_layer(Material_name, JV_curve, EQE_curve,Solar_Data))          # We append the Active_layer class with the current EQE_curve and JV_curve information as well as the material name within the Active_layers list


        # Otherwise if we just want to analyze one spectrum we must provide the location of both the JV curve file and the EQE curve file, which we will be prompted to select, as well as the solar data file necessary for calculations
        # The naming convention is still STRONGLY ENCOURAGED :3 since the name of the graph, and savefilename will be extracted from the name of the JV file
        else:
            EQE_curve = txtImp.import_txt(filedialog.askopenfilename(title='Select the EQE curve file of the spectrum you want to analyze', initialdir=r'C:\Users\minus\Documents\PhD\Rainbow\Curve data From enrique EQE',
                                                   filetypes=(('txt files', '*.txt'), ('All files', '*.*'))))  # Prompt the user to open a file that contains the EQE curve file of the spectrum to be analyzed, and import it as a txt file into the EQE_curve variable
            JV_file = filedialog.askopenfilename(title='Select the JV curve file of the spectrum you want to analyze', initialdir=r'C:\Users\minus\Documents\PhD\Rainbow\Curve data From enrique EQE',
                                                   filetypes=(('txt files', '*.txt'), ('All files', '*.*')))  # Prompt the user to open a file that contains the JV curve file of the spectrum to be analyzed
            JV_curve = txtImp.import_txt(JV_file)                                                                                                                          # We import it as a txt file into the JV_curve variable
            Solar_Data = txtImp.import_txt(filedialog.askopenfilename(title='Select the Solar Curve Spectrum file ', initialdir=r'C:\Users\minus\Documents\PhD\Rainbow\Curve data From enrique EQE',
                                                   filetypes=(('txt files', '*.txt'), ('All files', '*.*'))))  # Prompt the user to open a file that contains the Solar Curve txt files, and import it as a txt file into the Solar_Data variable
            Material_name = JV_file.split('_JV', 1)[0]
            Material_name = Material_name.split('/')[-1]                                                       # We split the full path provided and extract only the last part which corresponds to the material name

            # Finally we add the Material name the JV_curve and the EQE_curve into an Active_layer class for further processing and we set it into a list so that it can be processed in the same loop as it would if it were multiple spectra
            Active_layers = [AlC.Active_layer(Material_name, JV_curve, EQE_curve,Solar_Data)]

    # If we desire to save anything at all we will have to specify a saving directory
    if Save_Animation or Save_Animation_Individual_graphs or Save_Graphs:
        Save_Directory = filedialog.askdirectory(title='Select the directory where you want to save the resulting figures', initialdir=os.getcwd(), mustexist=True)  # Ask for the directory where all the resulting figures will be saved

    Timer1 = sf.Timer()                                      # We start a timer to keep track of the time
    Current_step = 0                                # We also initialize a current steps variable to further keep track of the progress and inform the user


    # Now we need to actually generate random EQE spectra and find the best matching spectra for the specified main spectrum
    # We will have to perform the math as many times as Spectra we have
    for Active_layer in Active_layers:

        current_min_enhancement_factor = 1                                  # We initialize a variable that will hold the performance of the lowest of the top performing EQE matches
        found_suitable_spectra = 0                                          # We set a counter to count the spectra that meet the minimum enhancement factor set in the beginning
        top_performing_matches_list = list()                                # We initialize a list that will hold the top performing EQE curves

        # For each main spectrum we will search for a match for as many iterations have been specified
        while found_suitable_spectra < minimum_suitable_spectra:

            # Now we generate a fresh random EQE curve with all the specified parameters that depend on each scenario
            # We set the FF to be similar to that of the active layer we are tackling so that it is easier to find a cell that successfully pairs up with the current active layer
            Random_EQE_curve = REG.Random_generated_EQE_curves(REG.EQE_Random_curve(max_EQE_value = min(80,round(max(sf.Extract_Column(Active_layer.EQE_curve,1)))+5),
                                                                                    max_Bgap = (1100 if Main_spectrum_blue_cell else 750),
                                                                                    min_Bgap=(750 if Main_spectrum_blue_cell else 400),
                                                                                    Normal_start_EQE_dist= True,
                                                                                    Normal_start_EQE_center=round(max(sf.Extract_Column(Active_layer.EQE_curve,1)))),
                                                               Solar_Data,
                                                               FF=max(Active_layer.FF,65))


            # We also set the Integrated_Jsc_correction factor of the random EQE to that of the Active layer to make the comparison more realistic
            Random_EQE_curve.Integrated_Jsc_correction_factor = Active_layer.Integrated_Jsc_correction_factor

            # If the EQE value is smaller than 25 just break the search because the EQE random generator will most likely not generate any matching spectra
            if max(sf.Extract_Column(Active_layer.EQE_curve,1)) < 25:
                break

            # now we pair them with the current Main spectrum and calculate their combined performance
            # If we set the main spectrum as the blue absorbing cell we set it in the following order
            if Main_spectrum_blue_cell:
                EQE_pair = AlC.Active_layer_Pair(Active_layer,Random_EQE_curve,Solar_Data)

            # and if we set the main spectrum as the red absorbing cell we set it in the reversed order
            else:
                EQE_pair = AlC.Active_layer_Pair(Random_EQE_curve, Active_layer, Solar_Data)
            # print(*EQE_pair.Eff_Dividing_wavelength_graph_total,sep = '\n')
            #
            # print('1st = ' + str(EQE_pair.Active_layer_1.Total_Eff)+' 2nd '+str(EQE_pair.Active_layer_2.Total_Eff))
            # print('Max enhanced efficiency = '+str(max(EQE_pair.Eff_Dividing_wavelength_graph_total)))
            # print('EQE Enhancement factor = '+str(EQE_pair.Eff_Enhancement_factor))



            # If the found spectrum fulfills the min enhancement factor requirement we log it as a suitable spectrum and then it passes on to the harder test of beating the currently best performing spectra
            if EQE_pair.Eff_Enhancement_factor > min_enhancement_factor:
                found_suitable_spectra += 1

            # If the current EQE_pair has an enhancement factor higher than the min_enhancement_factor specified and higher than the current_min_enhancement_factor then we proceed to append it to the list of top performing cells
            if EQE_pair.Eff_Enhancement_factor > min_enhancement_factor and EQE_pair.Eff_Enhancement_factor > current_min_enhancement_factor:

                # First we append it and then we resort fhe list with the new item taken into account
                top_performing_matches_list.append(EQE_pair)
                top_performing_matches_list.sort(key=operator.attrgetter('Eff_Enhancement_factor'))

                # If the list is longer than specified by the top_spectra_number we pop elements until it isn't longer than specified
                while len(top_performing_matches_list) > top_spectra_number:
                    top_performing_matches_list.pop()

                # Finally we take the lowest performing EQE_match and set its efficiency_enhancement_factor to be the new current_min_enhancement_factor
                top_performing_matches_list[-1].Eff_Enhancement_factor = current_min_enhancement_factor

            Current_step += 1                                                                                       # Keep track of the steps taken
            Timer1.Update_progress(found_suitable_spectra,minimum_suitable_spectra,True,True)                                                   # We update the timer at every iteration and set it to print the progress

            print('Suitable EQE curve found = '+str(found_suitable_spectra))

            # If we have enabled the debugging option we print the full analysis of the current EQE pair to check if it is working properly
            if Debugging:

                print('Random EQE curve Voc = '+str(Random_EQE_curve.Voc)+'    Voc loss = '+str(Random_EQE_curve.Voc_loss_constant)+'    Random EQE Jsc = '+str(Random_EQE_curve.Total_Jsc))
                print('Active layer Voc = ' + str(Active_layer.Voc) +'   Active layer Jsc = '+str(Active_layer.Jsc)+'   Active layer fill factor =  '+str(Active_layer.FF)+ '    Active layer calculated efficiency = ' + str(Active_layer.Total_Eff)+'   Active layer Real efficiency = ' + str((Active_layer.Voc*Active_layer.Jsc*Active_layer.FF)/100))

                # This part is only dedicated to plotting the compared EQE_curves
                gs = gridspec.GridSpec(2, 2)  # Create 2x2 sub plots and then span the third graph onto the lower two subplots

                # In the first subplot we plot the Efficiency vs Dividing wavelength for the current Material_pair

                fig = plt.figure(figsize=(12, 9))  # We set a big figure size so that we can actually see what is going on
                fig.suptitle('Full rainbow analysis for ' + str(EQE_pair.Full_Name), fontsize=16)
                ax1 = fig.add_subplot(gs[0, 0])  # row 0, col 0
                ax1.plot(EQE_pair.Dividing_wavelength_list, EQE_pair.Eff_Dividing_wavelength_graph_1, label=str(EQE_pair.Name_1st) + ' Efficiency',color= ('tab:blue' if Main_spectrum_blue_cell else 'tab:orange'))  # The first figure is the efficiency vs the dividing wavelength
                ax1.plot(EQE_pair.Dividing_wavelength_list, EQE_pair.Eff_Dividing_wavelength_graph_2, label=str(EQE_pair.Name_2nd) + ' Efficiency',color= ('tab:orange' if Main_spectrum_blue_cell else 'tab:blue'))
                ax1.plot(EQE_pair.Dividing_wavelength_list, EQE_pair.Eff_Dividing_wavelength_graph_total, label='Total Efficiency')
                ax1.set_title('Efficiency vs Dividing Wavelength')
                ax1.legend(loc='center right')
                ax1.set(xlabel='Dividing Wavelength /nm', ylabel='Efficiency /%')

                # In the second subplot we plot the Jsc vs Dividing wavelength for the current Material_pair
                ax2 = fig.add_subplot(gs[0, 1])  # row 0, col 1
                ax2.plot(EQE_pair.Dividing_wavelength_list,EQE_pair.Jsc_Dividing_wavelength_graph_1, label=str(EQE_pair.Name_1st) + ' Photocurrent',color= ('tab:blue' if Main_spectrum_blue_cell else 'tab:orange'))  # The second thing we plot is the Jsc vs Dividing wavelength
                ax2.plot(EQE_pair.Dividing_wavelength_list,EQE_pair.Jsc_Dividing_wavelength_graph_2, label=str(EQE_pair.Name_2nd) + ' Photocurrent',color= ('tab:orange' if Main_spectrum_blue_cell else 'tab:blue'))
                ax2.plot(EQE_pair.Dividing_wavelength_list,EQE_pair.Jsc_Dividing_wavelength_graph_total, label='Total Photocurrent')
                ax2.set_title('Jsc vs Dividing Wavelength')
                ax2.legend(loc='center right')
                ax2.set(xlabel='Dividing Wavelength /nm', ylabel='Jsc / mA * cm^-2')

                # In the third subplot we plot the EQE curves so that we can compare them when analyzing the data
                ax3 = fig.add_subplot(gs[1, :])  # row 1, span all columns
                ax3.plot(sf.Extract_Column(Active_layer.EQE_curve, 0), sf.Extract_Column(Active_layer.EQE_curve, 1), label=Active_layer.Name)  # The third thing we plot are the actual EQE curves
                ax3.plot(sf.Extract_Column(Random_EQE_curve.EQE_curve, 0), sf.Extract_Column(Random_EQE_curve.EQE_curve, 1), label=Random_EQE_curve.Name)
                ax3.set_title('EQE curves')
                ax3.legend(loc='upper right')
                ax3.set(xlabel='Wavelength /nm', ylabel='EQE /%')

                wavelength_list_active_layer = np.linspace(sf.Extract_Column(Active_layer.EQE_curve, 0)[0],sf.Extract_Column(Active_layer.EQE_curve, 0)[-1],len(Active_layer.Jsc_per_nm))
                wavelength_list_random_EQE = np.linspace(sf.Extract_Column(Random_EQE_curve.EQE_curve, 0)[0], sf.Extract_Column(Random_EQE_curve.EQE_curve, 0)[-1], len(Random_EQE_curve.Jsc_per_nm))

                # fig2 = plt.figure()
                # plt.plot(wavelength_list_active_layer, sf.Extract_Column(Active_layer.Jsc_per_nm, 1), label=Active_layer.Name)  # The third thing we plot are the actual EQE curves
                # plt.plot(wavelength_list_random_EQE, sf.Extract_Column(Random_EQE_curve.Jsc_per_nm, 1), label=Random_EQE_curve.Name)

                plt.show()
                time.sleep(2)
                plt.close('all')

        # If the EQE value is smaller than 25 continue to the next material and do not try to print anything because there will be no matching EQE curves
        if max(sf.Extract_Column(Active_layer.EQE_curve, 1)) < 25:
            print('Skipping '+str(Active_layer.Name)+' because of a low Max EQE value of '+str(max(sf.Extract_Column(Active_layer.EQE_curve, 1))))
            continue



        # Now we proceed to plot the resulting graphs, and if specified save them in separate directories and create animations
        colors = pl.cm.jet(np.linspace(0, 1, top_spectra_number))  # We set the color spectrum we will use for the plotting

        gs = gridspec.GridSpec(3, 2)  # Create 3x2 sub plots and then span the third graph onto the lower two subplots

        fig = plt.figure(figsize=(12, 9))  # We set a big figure size so that we can actually see what is going on
        plt.subplots_adjust(hspace=0.3,bottom=0,left=0.15)
        fig.suptitle('Best '+str(top_spectra_number)+' EQE curves for '+str(Active_layer.Name), fontsize=16)
        ax1 = fig.add_subplot(gs[0, 0])  # row 0, col 0                                                                                  # Plot one of the random generated curves
        for k in range(len(top_performing_matches_list)):
            ax1.plot(top_performing_matches_list[k].Dividing_wavelength_list, top_performing_matches_list[k].Eff_Dividing_wavelength_graph_total, color=colors[k])
        ax1.set_title('Total Efficiency vs dividing wavelength')
        ax1.set(xlabel='Dividing Wavelength /nm', ylabel='Efficiency /%')

        ax2 = fig.add_subplot(gs[0, 1])  # row 0, col 0                                                                                  # Plot one of the random generated curves
        for k in range(len(top_performing_matches_list)):
            ax2.plot(top_performing_matches_list[k].Dividing_wavelength_list,top_performing_matches_list[k].Jsc_Dividing_wavelength_graph_total, color=colors[k])
        ax2.set_title('Total Jsc vs dividing wavelength')
        ax2.set(xlabel='Dividing Wavelength /nm', ylabel='Jsc / mA * cm^-2')


        if Main_spectrum_blue_cell:
            ax3 = fig.add_subplot(gs[1, :])  # row 1, span all columns
            ax3.plot(sf.Extract_Column(top_performing_matches_list[0].Active_layer_1.EQE_curve, 0), sf.Extract_Column(top_performing_matches_list[0].Active_layer_1.EQE_curve, 1), label=('Original EQE spectrum'), color=(0,0,0))
            for k in range(len(top_performing_matches_list)):
                ax3.plot(sf.Extract_Column(top_performing_matches_list[k].Active_layer_2.EQE_curve, 0), sf.Extract_Column(top_performing_matches_list[k].Active_layer_2.EQE_curve, 1), color=colors[k])
                print('Voc = ' + str(round(top_performing_matches_list[k].Active_layer_2.Voc,2)) + '   Jsc = ' + str(round(top_performing_matches_list[k].Active_layer_2.Total_Jsc,2)) + '   FF = ' + str(top_performing_matches_list[k].Active_layer_1.FF))
            ax3.set_title('EQE curves')
            ax3.legend(loc='upper right')
            ax3.set(xlabel='Wavelength /nm', ylabel='EQE /%')

            # We also plot a table with the Jsc Voc and FF values of the Randomly generated EQE curves

            # First we store the different variables on a 2d list
            data = list()
            attribute_list = ['Voc', 'Total_Jsc', 'FF']
            for attribute in attribute_list:
                temp_list = list()
                for k in range(len(top_performing_matches_list)):
                    temp_list.append(round(getattr(top_performing_matches_list[k].Active_layer_2, attribute),2))
                data.append(temp_list)

            # We also need to store the efficiency values of the randomly generated EQE curves
            temp_list = list()
            for k in range(len(top_performing_matches_list)):
                temp_list.append(round((top_performing_matches_list[k].Active_layer_2.Voc * top_performing_matches_list[k].Active_layer_2.Total_Jsc *top_performing_matches_list[k].Active_layer_2.Integrated_Jsc_correction_factor* top_performing_matches_list[k].Active_layer_2.FF / 100),2))
            data.append(temp_list)

            # We set the names of the rows and columns
            rows = ['Voc (V)', 'Jsc (mA*cm^-2)', 'FF (%)', 'Eff (%)']
            columns = ['EQE %d' % x for x in range(len(top_performing_matches_list))]

            # And finally we plot the table
            table = fig.add_subplot(gs[2, :])  # row 1, span all columns
            table.axis('off')
            the_table = table.table(cellText=data,
                                    rowLabels=rows,
                                    colColours=colors,
                                    colLabels=columns,
                                    loc='center')

            # We will also add a label informing about the Bgap of the original spectrum and the Voc loss of this particular cell
            # Voc_loss_label = 'Real spectrum Bgap = ' + str(round((top_performing_matches_list[0].Active_layer_1.Eg),3)) + '  eV    Voc loss = '+str(round((top_performing_matches_list[0].Active_layer_1.Eg-top_performing_matches_list[0].Active_layer_1.Voc),3)) + ' V'
            # table.text(0.27, 0.9, Voc_loss_label, ha='left', wrap=True)

        else:
            ax3 = fig.add_subplot(gs[1, :])  # row 1, span all columns
            ax3.plot(sf.Extract_Column(top_performing_matches_list[0].Active_layer_2.EQE_curve, 0), sf.Extract_Column(top_performing_matches_list[0].Active_layer_2.EQE_curve, 1), label=('Original EQE spectrum'), color=(0, 0, 0))
            for k in range(len(top_performing_matches_list)):
                ax3.plot(sf.Extract_Column(top_performing_matches_list[k].Active_layer_1.EQE_curve, 0), sf.Extract_Column(top_performing_matches_list[k].Active_layer_1.EQE_curve, 1), color=colors[k])
                print('Voc = ' + str(round(top_performing_matches_list[k].Active_layer_1.Voc,2))+'   Jsc = '+ str(round(top_performing_matches_list[k].Active_layer_1.Total_Jsc,2))+'   FF = '+ str(top_performing_matches_list[k].Active_layer_1.FF))
            ax3.set_title('EQE curves')
            ax3.legend(loc='upper right')
            ax3.set(xlabel='Wavelength /nm', ylabel='EQE /%')

            # We also plot a table with the Jsc Voc and FF values of the Randomly generated EQE curves

            # First we store the different variables on a 2d list
            data = list()
            attribute_list = ['Voc', 'Total_Jsc','FF']
            for attribute in attribute_list:
                temp_list = list()
                for k in range(len(top_performing_matches_list)):
                    temp_list.append(round(getattr(top_performing_matches_list[k].Active_layer_1, attribute),2))
                data.append(temp_list)

            # We also need to store the efficiency values of the randomly generated EQE curves
            temp_list = list()
            for k in range(len(top_performing_matches_list)):
                temp_list.append(round((top_performing_matches_list[k].Active_layer_1.Voc*top_performing_matches_list[k].Active_layer_1.Total_Jsc*top_performing_matches_list[k].Active_layer_1.Integrated_Jsc_correction_factor*top_performing_matches_list[k].Active_layer_1.FF/100),2))
            data.append(temp_list)

            # We set the names of the rows and columns
            rows = ['Voc (V)', 'Jsc (mA*cm^-2)','FF (%)','Eff (%)']
            columns = ['EQE %d' % x for x in range(len(top_performing_matches_list))]

            # And finally we plot the table
            table = fig.add_subplot(gs[2, :])  # row 1, span all columns
            table.axis('off')
            the_table = table.table(cellText=data,
                                    rowLabels=rows,
                                    colColours=colors,
                                    colLabels=columns,
                                    loc='center')

            # We will also add a label informing about the Bgap of the original spectrum and the Voc loss of this particular cell
            # Voc_loss_label = 'Real spectrum Bgap = ' + str(round((top_performing_matches_list[0].Active_layer_2.Eg), 3)) + '  (eV)    Voc loss = ' + str(round((top_performing_matches_list[0].Active_layer_2.Eg - top_performing_matches_list[0].Active_layer_2.Voc), 3)) + ' V'
            # table.text(0.27, 0.9, Voc_loss_label, ha='left', wrap=True)


        # Finally we set the figure name with the directory we want to save it to and we save and close all the figures open to continue through the loop
        fig_name = ' Best Match EQE curves for ' + str(Active_layer.Name) + '.png'
        fig_name = sf.Full_path_adder(fig_name, Save_Directory)
        plt.savefig(fig_name)
        # plt.show()
        plt.close('all')

