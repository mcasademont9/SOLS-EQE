
# --------------------------------------------- This scripts main function is to create two top hat eqe curves and compare their binary rainbow efficiencies while widening one of the EQE curves with respect to the other
# --------------------------------------------- It performs this operation for different starting EQE widths and then plots the efficiency enhancement for each starting width with an animation and the enhancement factor per width difference and per width difference ratio

import matplotlib.pyplot as plt                                                                     # First we import the necessary libraries and scripts from the project
import Small_Functions as sf
import Random_EQE_Generator as REG
import Text_Importer as txtImp
import matplotlib.gridspec as gridspec
from tkinter import filedialog
import os
import imageio
from Two_Sliding_EQE_curves import EQE_Top_Hat_curve
import numpy as np
import matplotlib.pylab as pl


if __name__ == '__main__':

    # First we set the desired features of the software
    Output_animation = True                                                # If we want to output an animation of the curves evolving we will have to provide a directory where to save the images and the animation
    Save_animation_frame_by_frame_graphs = False
    Save_graphs = True                                                     # IF a part from an animation we want to save the animation images we set this value to true, also if we want to save any of the generated graphs

    Constant_area = True                                                  # We can also set a constant area parameter where each time the eqe curve widens its maximum value decreases starting at high EQE values and subsequently getting lower as it widens, keeping the area constant


    # First we fetch the solar irradiance spectrum from a predefined location or ask the user to give us the location of the file
    try:
        Solar_TXT = r'C:\Users\minus\Documents\PhD\Rainbow\Solar Curve.txt'                                                 # We load the solar radiance spectrum located in this directory if it exists
        Solar_Data = txtImp.import_txt(Solar_TXT)  # Import the Solar curve data into the Solar_Data Variable
    except FileNotFoundError:                                                                                               # If we do not find the solar spectrum in the specified folder we prompt the user to give us the current location
        Solar_TXT = filedialog.askopenfilename(title='Select the Solar Curve Spectrum TXT ', initialdir=os.getcwd(), filetypes=(('txt files', '*.txt'), ('All files', '*.*')))  # Prompt the user to open a file that contains the Solar Curve txt files, and assign the file path to the variable Solar_TXT
        Solar_Data = txtImp.import_txt(Solar_TXT)  # Import the Solar curve data into the Solar_Data Variable

    # If we want to save the animation or the images of the animation we will need a save directory
    if Output_animation or Save_graphs:
        Save_Directory = filedialog.askdirectory(title='Select the directory where you want to save the resulting figures', initialdir=r'C:\Users\minus\Documents\PhD\Rainbow\Figures', mustexist=True)  # Ask for the directory where all the resulting figures will be saved

    Timer1 = sf.Timer()                                                         # We first initialize a timer to measure the progress and the estimated and elapsed time

    # Here we set how many stationary width values we want to measure and how many different widths differences per static EQE width we want to measure
    # The higher the number of different widths differences the finer the resulting graph will be but the longer the process will take
    Total_stationary_EQE_width_values = 8                          # 8
    Total_width_difference_values = 100                             # 100

    # We also set the EQE curve parameters, the EQE_curve_width_difference will adapt to the specified range dividing it into the number of specified values
    Min_EQE_Width_difference = 50
    Max_EQE_Width_difference = 900
    # We also set the EQE curve separation parameters, the Total_stationary_EQE_width_values will adapt to the specified range dividing it into the number of specified values
    Min_EQE_Stationary_width = 50
    Max_EQE_Stationary_width = 400
    # We also set a Reference bandgap from with all values will start, basically this will be the band gap of all stationary EQE curves regardless of their width
    Reference_Bgap = 600
    # Finally we set the maximum EQE height value at which each curve will start, we set it rather high to prevent the curves from disappearing too fast. We also declare the EQE static height.
    EQE_max_initial_height = 90
    EQE_static_height = 65

    # We also set a Reference bandgaps from with all values will start, basically this will be the band gap of all stationary EQE curves regardless of their width
    # We set a list of bandgaps that will be tested, there will be a full report for each and everyone of them
    Total_Bgap_values = [600]#[500,600,700,800,900]
    Min_Bgap = 400                                              # We also set a Minimum bgap from which all the EQE curves will start sliding

    # We also initialize some variables that will be of use latter
    Saved_figures = 0                                                                   # The saved figures will help us track progress of the program
    Total_figures = Total_stationary_EQE_width_values * Total_width_difference_values * len(Total_Bgap_values)                # We calculate the total number of figures to keep track of the progress

    # We also have to set the total clip duration of the animation in seconds
    Total_clip_duration = 20
    Frame_duration = Total_clip_duration / Total_width_difference_values

    # We loop through every selected static Bgap and generate a full report fer each
    for Reference_Bgap in Total_Bgap_values:

        # We redefine max EQE separation with every band gap to cover the whole
        Stationary_width_values_list = list()  # The width_values_list will be used for the plotting of the EQE_enhancement factor
        EQE_enhancement_list = [list() for i in range(Total_stationary_EQE_width_values)]  # We initialize a list with lists for each different width value that will hold all the curves comparisons. We need to initialize it every time we start with a different bangap

        if Output_animation or Save_graphs:
            Current_Bgap_save_directory = sf.Full_path_adder(('EQE Bgap ' + str(Reference_Bgap)) + ' nm', Save_Directory)
            if not os.path.exists(Current_Bgap_save_directory):
                os.mkdir(Current_Bgap_save_directory)

        # Now we loop through each width value and we calculate the EQE curve widening for each specified stateic EQE width value and calculate the enhancement factor at each EQE width difference and store it for further plotting
        for j in range(Total_stationary_EQE_width_values):

            Static_EQE_width = round(Min_EQE_Stationary_width + (sf.division_possible_zero(j, (Total_stationary_EQE_width_values - 1))) * (Max_EQE_Stationary_width - Min_EQE_Stationary_width))       # We set the static EQE width value according to the parameters we have set before and for each subsequent loop we increase the value of the static EQE width until we reach the Max value specified
            Stationary_width_values_list.append(Static_EQE_width)                                                                                     # We also store the set EQE_width value for further plotting

            # If we chose Output_animation = True, we create different folders to save each static EQE width animation images and animations
            if Output_animation:
                Current_static_width_save_directory = sf.Full_path_adder(('EQE width ' + str(Static_EQE_width)) + ' nm', Current_Bgap_save_directory)
                if not os.path.exists(Current_static_width_save_directory):
                    os.mkdir(Current_static_width_save_directory)

                # We also initialize a list that will hold the image file list to create the animation for each static EQE width
                Image_file_list = list()

            # Now, for a specified Static_EQE_width value we loop, widening one of the EQE curves, and measuring the resulting EQE efficiency for as many times as specified by the Total_width_difference_values variable.
            for i in range(Total_width_difference_values):

                if Constant_area and i == 0:
                    # This is the minimum bandgap the widening EQE can have to prevent it from having a higher value than the specified EQE_max_initial_value
                    Min_widening_Bgap = ((Static_EQE_width*EQE_static_height)/EQE_max_initial_height)+(Reference_Bgap-Static_EQE_width)
                    Min_EQE_Width_difference = Min_widening_Bgap-Reference_Bgap
                    EQE_curve_constant_area = Static_EQE_width*EQE_static_height

                # We set the current EQE_curve_width_difference according to the previously specified values, we start on the minimum value and for each subsequent loop we increase the separation by a calculated amount.
                # We also measure the EQE_curve_width_difference_normalized to the Static_EQE_width to search for the optimal ratio of EQE width
                EQE_curve_width_difference = Min_EQE_Width_difference + ((sf.division_possible_zero(i,(Total_width_difference_values-1))) * (Max_EQE_Width_difference - Min_EQE_Width_difference))
                Widening_EQE_curve_width_normalized = (Static_EQE_width + (Min_EQE_Width_difference + ((sf.division_possible_zero(i,(Total_width_difference_values-1))) * (Max_EQE_Width_difference - Min_EQE_Width_difference)))) / Static_EQE_width         # This is the ratio Total EQE width/ Static EQE width
                Widening_EQE_current_width = max(0,Static_EQE_width + EQE_curve_width_difference)

                # We generate two EQE top hat curves that differ only on the EQE width and we store them in a Random_generated_EQE_curves class. Even if this class is not specifically intended to store this kind of curve it works perfectly specially for the following calculations
                EQE1 = REG.Random_generated_EQE_curves(EQE_Top_Hat_curve(Bgap = Reference_Bgap,EQE_width = Static_EQE_width,EQE_value=EQE_static_height),Solar_Data)
                EQE2 = REG.Random_generated_EQE_curves(EQE_Top_Hat_curve(Bgap = Reference_Bgap + EQE_curve_width_difference,EQE_width = Widening_EQE_current_width,EQE_value = ((sf.division_possible_zero(EQE_curve_constant_area,Widening_EQE_current_width)) if Constant_area else EQE_static_height)),Solar_Data)

                # We now store the EQE curve pair in a Random_generated_EQE_Pair class since this class performs the necessary calculations when provided two Random_generated_EQE_curves and the solar irradiance spectrum data
                EQE_pair = REG.Random_generated_EQE_Pair(EQE1,EQE2,Solar_Data)

                # We now store the Enhancement factor as well as the EQE_curve_width_difference and EQE_curve_width_difference_normalized for further plotting. We avoid the EQE_curve_width_difference_normalized == 0 value because we are plotting on a log scale and the curves significantly distort when this value is not avoided
                EQE_enhancement_list[j].append([EQE_curve_width_difference,Widening_EQE_curve_width_normalized,EQE_pair.Eff_Enhancement_factor,max(EQE_pair.Eff_Dividing_wavelength_graph_total)])

                if i == 0:
                    # We calculate the maximum efficiency of the EQE curve will have by doubling the max efficiency of the static curve
                    if Constant_area:
                        EQE_Max = REG.Random_generated_EQE_curves(EQE_Top_Hat_curve(Bgap=(635 + (Static_EQE_width / 2)), EQE_width=Static_EQE_width,EQE_value=EQE_static_height), Solar_Data)

                    # Or in the case the area is not constant we just take a 300 nm wide EQE curve reference
                    else:
                        EQE_Max = REG.Random_generated_EQE_curves(EQE_Top_Hat_curve(Bgap=(635 + (300 / 2)), EQE_width=300, EQE_value=EQE_static_height), Solar_Data)
                    Max_efficiency_value = EQE_Max.Total_Eff * 2
                    Max_Jsc_value = EQE_Max.Total_Jsc * 2

                if Output_animation:

                    # If we chose to output an animation we need to generate the necessary graphs for each EQE_curve_width_difference
                    # In this section we set the necessary graphs
                    gs = gridspec.GridSpec(2, 2)            # Create 2x2 sub plots and then span the third graph onto the lower two subplots

                    fig = plt.figure(figsize=(12, 9))  # We set a big figure size so that we can actually see what is going on
                    fig.suptitle('Two Widening EQE curves compared'+(' with Constant Area' if Constant_area else '')+', static EQE width '+str(Static_EQE_width)+' nm', fontsize=16)
                    ax1 = fig.add_subplot(gs[0, 0])  # row 0, col 0
                    ax1.plot(EQE_pair.Dividing_wavelength_list, EQE_pair.Eff_Dividing_wavelength_graph_1, label='EQE 1 Efficiency')  # The first figure is the efficiency vs the dividing wavelength
                    ax1.plot(EQE_pair.Dividing_wavelength_list, EQE_pair.Eff_Dividing_wavelength_graph_2, label='EQE 2 Efficiency')
                    ax1.plot(EQE_pair.Dividing_wavelength_list, EQE_pair.Eff_Dividing_wavelength_graph_total, label='Total Efficiency')
                    ax1.set_title('Efficiency vs Dividing Wavelength')
                    ax1.set_ylim(top=Max_efficiency_value, bottom=0)
                    ax1.legend(loc='center right')
                    ax1.set(xlabel='Dividing Wavelength /nm', ylabel='Efficiency /%')

                    ax2 = fig.add_subplot(gs[0, 1])  # row 0, col 1
                    ax2.plot(EQE_pair.Dividing_wavelength_list, EQE_pair.Jsc_Dividing_wavelength_graph_1, label='EQE 1 Jsc')  # The second thing we plot is the Jsc vs Dividing wavelength
                    ax2.plot(EQE_pair.Dividing_wavelength_list, EQE_pair.Jsc_Dividing_wavelength_graph_2, label='EQE 2 Jsc')
                    ax2.plot(EQE_pair.Dividing_wavelength_list, EQE_pair.Jsc_Dividing_wavelength_graph_total, label='Total Jsc')
                    ax2.set_title('Jsc vs Dividing Wavelength')
                    ax2.set_ylim(top=Max_Jsc_value,bottom=0)
                    ax2.legend(loc='center right')
                    ax2.set(xlabel='Dividing Wavelength /nm', ylabel='Jsc / mA * cm^-2')

                    ax3 = fig.add_subplot(gs[1, :])  # row 1, span all columns
                    ax3.plot(sf.Extract_Column(EQE1.EQE_curve, 0), sf.Extract_Column(EQE1.EQE_curve, 1), label='EQE 1')  # The third thing we plot are the actual EQE curves
                    ax3.plot(sf.Extract_Column(EQE2.EQE_curve, 0), sf.Extract_Column(EQE2.EQE_curve, 1), label='EQE 2')
                    ax3.set_title('EQE values')
                    ax3.legend(loc='upper right')
                    ax3.set(xlabel='Wavelength /nm', ylabel='EQE /%')

                    # Finally we set the figure name with the directory we want to save it to and we save and close all the figures open to continue through the loop
                    fig_name = ' Binary rainbow widening EQE curve ' + str(Saved_figures) + '.png'
                    fig_name = sf.Full_path_adder(fig_name, Current_static_width_save_directory)
                    # print(fig_name)
                    plt.savefig(fig_name)
                    plt.close('all')

                    Image_file_list.append(fig_name)                                                        # We append the image full path to the image file list to create the animation afterwards

                # We also want to keep the user informed about the progress of the file conversion so we update the timer at every loop and print an informative message
                Saved_figures += 1  # We update the counter every time we save a figure

                # Finally we print an informative message for the user informing about the progress of the calculation
                Timer1.Update_progress(Saved_figures, Total_figures,kronos=True,Print_progress=True)  # And we also update the progress value  # And we also update the progress value


            if Output_animation:
                # We finally take the image list and create a gif with the specified duration and save it in the current width directory
                with imageio.get_writer(sf.Full_path_adder(('Binary rainbow widening EQE curves'+(' with Constant Area' if Constant_area else '')+' animation '+str(Static_EQE_width)+' nm.gif'),Current_Bgap_save_directory), mode='I', duration=Frame_duration) as writer:
                    for filename in Image_file_list:
                        image = imageio.imread(filename)
                        writer.append_data(image)

                # If we have selected not to save the animation graphs we delete all files within the current width directory as well as the directory itself
                if not Save_animation_frame_by_frame_graphs:
                    for file in Image_file_list:
                        os.remove(file)
                    os.rmdir(Current_static_width_save_directory)


        # Finally we plot the enhancement graphs for each static EQE width and the ones that have been normalized on a multisubplot and if enabled we save it on a png file
        gs = gridspec.GridSpec(2, 1)

        colors = pl.cm.jet(np.linspace(0, 1, Total_stationary_EQE_width_values))                                                                # We set the color spectrum we will use for the plotting

        fig = plt.figure(figsize=(12, 9))                                                                                          # We set a big figure size so that we can actually see what is going on
        plt.subplots_adjust(hspace=0.3)
        fig.suptitle('Multiple static width EQE curve efficiency enhancement factor analysis with'+str(Reference_Bgap)+' nm Bgap'+(' and Constant Area' if Constant_area else ''), fontsize=16)
        ax1 = fig.add_subplot(gs[0, 0]) # row 0, col 0                                                                                  # Plot one of the random generated curves
        for k in range(Total_stationary_EQE_width_values):
            ax1.plot(sf.Extract_Column(EQE_enhancement_list[k],0),sf.Extract_Column(EQE_enhancement_list[k],2),label= ('Static EQE width '+str(round(Stationary_width_values_list[k]))+' nm'),color = colors[k] )
        ax1.set_title('Efficiency enhancement for one widening and one static EQE curves')
        ax1.legend(loc='upper left')
        ax1.set_xlim(left=-250)
        ax1.set(xlabel='EQE Width difference /nm', ylabel='Efficiency enhancement factor /x')

        ax2 = fig.add_subplot(gs[1, 0]) # row 0, col 0                                                                                  # Plot one of the random generated curves
        for k in range(Total_stationary_EQE_width_values):
            ax2.plot(sf.Extract_Column(EQE_enhancement_list[k],1),sf.Extract_Column(EQE_enhancement_list[k],2),label= ('Static EQE width '+str(round(Stationary_width_values_list[k]))+' nm'),color = colors[k])
        ax2.set_title('Efficiency enhancement for one widening and one static EQE curves, normalized')
        ax2.legend(loc='upper left')
        ax2.set(xlabel='EQE Width difference/Static EQE Width /nm', ylabel='Efficiency enhancement factor /x')
        ax2.set_xlim(left=0.4)  # set the xlim to left, right
        ax2.set_xscale('log')
        # ax2.set_xlim(left=0.1)  # set the xlim to left, right

        if Save_graphs:
            # Finally we set the figure name with the directory we want to save it to and we save and close all the figures open to continue through the loop
            fig_name = 'Binary rainbow widening EQE curve enhancement factor per width per width.png'
            fig_name = sf.Full_path_adder(fig_name, Current_Bgap_save_directory)
            # print(fig_name)
            plt.savefig(fig_name)


        # Finally we also plot the maximum efficiency graphs for each EQE width and the ones that have been normalized on a multisubplot and if enabled we save it on a png file
        gs2 = gridspec.GridSpec(2, 1)

        fig2 = plt.figure(figsize=(12, 9))  # We set a big figure size so that we can actually see what is going on
        plt.subplots_adjust(hspace=0.3)
        fig2.suptitle('Multiple static width EQE curve maximum efficiency analysis with'+str(Reference_Bgap)+' nm Bgap'+(' and Constant Area' if Constant_area else ''), fontsize=16)
        ax1 = fig2.add_subplot(gs[0, 0]) # row 0, col 0                                                                                  # Plot one of the random generated curves
        for k in range(Total_stationary_EQE_width_values):
            ax1.plot(sf.Extract_Column(EQE_enhancement_list[k],0),sf.Extract_Column(EQE_enhancement_list[k],3),label= ('Static EQE width '+str(round(Stationary_width_values_list[k]))+' nm'),color = colors[k],linestyle='-.' )
        ax1.set_title('Total maximum efficiency for one widening and one static EQE curves')
        ax1.legend(loc='upper right')
        ax1.set(xlabel='EQE Width difference /nm', ylabel='Total maximum efficiency /%')

        ax2 = fig2.add_subplot(gs[1, 0]) # row 0, col 0                                                                                  # Plot one of the random generated curves
        for k in range(Total_stationary_EQE_width_values):
            ax2.plot(sf.Extract_Column(EQE_enhancement_list[k],1),sf.Extract_Column(EQE_enhancement_list[k],3),label= ('Static EQE width '+str(round(Stationary_width_values_list[k]))+' nm'),color = colors[k],linestyle='-.')
        ax2.set_title('Total maximum efficiency for one widening and one static EQE curves, normalized')
        ax2.legend(loc='upper right')
        ax2.set(xlabel='EQE Width difference/Static EQE Width /nm', ylabel='Total maximum efficiency /%')
        ax2.set_xscale('log')
        # ax2.set_xlim(left=0.1)  # set the xlim to left, right

        if Save_graphs:
            # Finally we set the figure name with the directory we want to save it to and we save and close all the figures open to continue through the loop
            fig_name = 'Binary rainbow widening EQE curve total maximum efficiency per width.png'
            fig_name = sf.Full_path_adder(fig_name, Current_Bgap_save_directory)
            # print(fig_name)
            plt.savefig(fig_name)


        # plt.show()
        plt.close('all')