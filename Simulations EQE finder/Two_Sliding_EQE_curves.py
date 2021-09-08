
# ------------------------------------------ The main function of this script is to generate two identical EQE curves of a set width, that can be specified and even varied
# ------------------------------------------ and then slide one of them and calculate the resulting total solar cell efficiency for each EQE separation
# ------------------------------------------ This procedure can be performed for different EQE widths and It can all be exported as an animation or set of images, as well as a graph that calculates
# ------------------------------------------ the enhancement factor at each wavelength separation

import numpy as np                                                      # First we import the necessary libraries for the defined functions

# This first function generates a random EQE curve that starts at min_x and ends at max_x and whose value can oscillate between max_EQE_value and min_EQE_value. Its bandgap can oscillate between min_Bgap and max_Bgap.
# The basic shape of the EQE starts with a sigmoid at 300 nm and it reaches the starting EQE value which is set to be between the max_EQE_value and the min_EQE_value and then it oscillates as it progresses randomly
# through the spectrum trying to minimize big sudden changes and then when it reaches the bandgap (which has been assigned randomly within the range) it drops suddenly with the shape of another sigmoid
def EQE_Top_Hat_curve(min_wavelength = 300,max_wavelength = 1100,Bgap = 600, EQE_width = 250 ,EQE_value = 60,):     # This function does not need any argument but it can accept many, to define the precise limits for the generation of the EQE curves

    # First we generate the linear space that will hold the wavelength_list so that the EQE values have a wavelength reference
    wavelength_list = np.linspace((min_wavelength), (max_wavelength), (max_wavelength) - (min_wavelength) + 1)                          # We generate a linear space that will be offset 100 points to each side and it will be comprised of n values one for each wavelength integer within the range

    # We now prepare the function that will be multiplied to the random values to result in the shape of a more or less realistic EQE curve. It is basically a top hat function that instead of raising sharply it raises and falls with the shape of a sigmoid
    EQE_curve = list()                                                                                                                                         # We initialize the list that will contain all the top hat sigmoid values
    sigmoid_expansion_constant_low = 0.1                                                                                                                        # We set the sigmoid width factor of the raising sigmoid (The lower the coefficient the more spread it becomes)
    sigmoid_expansion_constant_high = 0.1                                                                                                                       # We set the sigmoid width factor of the falling sigmoid (The lower the coefficient the more spread it becomes)
    for wavelength in wavelength_list:                                                                                                                          # We loop through the wavelength_list and assign a multiplying factor to each wavelength value according to the two sigmoid functions
        # The sigmoid function is basically composed of two sigmoid functions multiplied, The first one is a sigmoid function that raises from 0 to 1, 50 nm higher than the min_wavelength, and the other sigmoid function falls exactly at the Bgap_value from 1 to 0
        Sigmoid_value = (1 / (1 + np.exp(sigmoid_expansion_constant_high * (-wavelength + (Bgap-EQE_width))))*(1-(1 / (1 + np.exp(sigmoid_expansion_constant_low * (-wavelength + Bgap))))))  # We store the value within a temporal variable
        EQE_curve.append([wavelength,(Sigmoid_value*EQE_value)])                                                                                                                        # When the value has been calculated we append it to the Bg_sigmoid list for further processing

    return EQE_curve,Bgap                                                                            # Finally we return the EQE_curve


# ---------------------------------------------------------------------------------------- Main script ---------------------------------------------------

import matplotlib.pyplot as plt                                                                     # First we import the necessary libraries and scripts from the project
import Small_Functions as sf
import Random_EQE_Generator as REG
import Text_Importer as txtImp
import matplotlib.gridspec as gridspec
from tkinter import filedialog
import os
import imageio
import matplotlib.pylab as pl


if __name__ == '__main__':

    # First we set the desired features of the software
    Output_animation = True                                                # If we want to output an animation of the curves evolving we will have to provide a directory where to save the images and the animation
    Save_animation_graphs =False                                           # IF a part from an animation we want to save the animation images we set this value to true
    Save_graphs = True                                                     # If we want to save any of the generated full report graphs


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

    # Here we set how many width values we want to measure and how many different Bgap differences per width we want to measure
    # The higher the number of Bgap differences the finer the resulting graph will be but the longer the process will take
    Total_width_values = 8                                             # 8
    Total_EQE_peak_separation_values = 100                               # 100

    # We also set the EQE curve parameters, the Total_width_values will adapt to the specified range dividing it into the number of specified values
    Min_EQE_Width = 50
    Max_EQE_Width = 400
    # We also set the EQE curve separation parameters, the Total_diff_Bgap_values will adapt to the specified range dividing it into the number of specified values
    # Min_EQE_Separation = 0                                    # Deprecated because of relative min EQE separation added afterwards
    Max_EQE_Separation = 800
    # We also set a Reference bandgaps from with all values will start, basically this will be the band gap of all stationary EQE curves regardless of their width
    # We set a list of bandgaps that will be tested, there will be a full report for each and everyone of them
    Total_Bgap_values = [400,500,600,700,800,900]
    Min_Bgap = 400                                              # We also set a Minimum bgap from which all the EQE curves will start sliding

    # We also initialize some variables that will be of use latter
    Saved_figures = 0                                                                   # The saved figures will help us track progress of the program
    Total_figures = Total_width_values * Total_EQE_peak_separation_values * len(Total_Bgap_values)         # We calculate the total number of figures to keep track of the progress

    # We also have to set the total clip duration of the animation in seconds
    Total_clip_duration = 20
    Frame_duration = Total_clip_duration / Total_EQE_peak_separation_values

    # We loop through every selected static Bgap and generate a full report fer each
    for Reference_Bgap in Total_Bgap_values:

        # We redefine max EQE separation with every band gap to cover the whole
        width_values_list = list()                                          # The width_values_list will be used for the plotting of the EQE_enhancement factor We need to initialize it every time we start with a different bangap
        EQE_enhancement_list = [list() for i in range(Total_width_values)]  # We initialize a list with lists for each different width value that will hold all the curves comparisons. We need to initialize it every time we start with a different bangap

        if Output_animation or Save_graphs:
            Current_Bgap_save_directory = sf.Full_path_adder(('EQE Bgap ' + str(Reference_Bgap)) + ' nm', Save_Directory)
            if not os.path.exists(Current_Bgap_save_directory):
                os.mkdir(Current_Bgap_save_directory)

        # Now we loop through each width value and we calculate the EQE curve slide for each specified width value and calculate the enhancement factor at each EQE peak separation and store it for further plotting
        for j in range(Total_width_values):

            EQE_width = Min_EQE_Width + (sf.division_possible_zero(j, (Total_width_values - 1))) * (Max_EQE_Width - Min_EQE_Width)       # We set the EQE width value according to the parameters we have set before and for each subsequent loop we increase the value of the EQE width until we reach the Max value specified
            width_values_list.append(EQE_width)                                                                                     # We also store the set EQE_width value for further plotting

            # If we chose Output_animation = True, we create different folders to save each EQE width animation images and animations
            if Output_animation:
                Current_width_save_directory = sf.Full_path_adder(('EQE width ' + str(EQE_width)) + ' nm', Current_Bgap_save_directory)
                if not os.path.exists(Current_width_save_directory):
                    os.mkdir(Current_width_save_directory)

                # We also initialize a list that will hold the image file list to create the animation for each EQE width
                Image_file_list = list()

            # Now, for a specified EQE_width value we loop, sliding one of the EQE curves, and measuring the resulting EQE efficiency for as many times as specified by the Total_diff_Bgap_values variable.
            for i in range(Total_EQE_peak_separation_values):

                # Now we define the minimum EQE as the minimum bgap we want to explore minus the reference bandgap we are currently in, this way the curve will always start on the same wavelength regardless of the EQE separation
                # because as the Reference Bgap gets bigger the Min EQE separation gets more negative bringing the starting value back to the Min_Bgap value
                Min_EQE_Separation = Min_Bgap-Reference_Bgap

                # We set the current EQE peak separation according to the previously specified values, we start on the minimum value and for each subsequent loop we increase the separation by a calculated ammount.
                # We also measure the peak separation normalized to the EQE_width to search for the optimal value of EQE separation
                EQE_peak_separation = Min_EQE_Separation + ((sf.division_possible_zero(i,(Total_EQE_peak_separation_values-1))) * (Max_EQE_Separation - Min_EQE_Separation))
                # Since we are plotting the EQE_peak_position_per_width on a logarithmic scale it does not make sense to store the negative values so we store them all (only the negatives) as 0
                EQE_peak_separation_per_width = max(0,(EQE_peak_separation / EQE_width))

                # We generate two EQE top hat curves separated only by the current EQE_peak_separation and we store them in a Random_generated_EQE_curves class. Even if this class is not specifically intended to store this kind of curve it works perfectly specially for the following calculations
                EQE1 = REG.Random_generated_EQE_curves(EQE_Top_Hat_curve(Bgap = Reference_Bgap,EQE_width = EQE_width),Solar_Data)
                EQE2 = REG.Random_generated_EQE_curves(EQE_Top_Hat_curve(Bgap = EQE_peak_separation + Reference_Bgap,EQE_width = EQE_width),Solar_Data)


                # We now store the EQE curve pair in a Random_generated_EQE_Pair class since this class performs the necessary calculations when provided two Random_generated_EQE_curves and the solar irradiance spectrum data
                EQE_pair = REG.Random_generated_EQE_Pair(EQE1,EQE2,Solar_Data)

                # We now store the Enhancement factor as well as the EQE_peak_separation and EQE_peak_separation_per_width for further plotting. We avoid the EQE_peak_separation_per_width == 0 value because we are plotting on a log scale and the curves significantly distort when this value is not avoided
                # We have also added an append for the maximum efficiency value te keep track of the absolute best parameters for the EQE overlapping
                EQE_enhancement_list[j].append([EQE_peak_separation,EQE_peak_separation_per_width,EQE_pair.Eff_Enhancement_factor,max(EQE_pair.Eff_Dividing_wavelength_graph_total)])

                # On the first loop we calculate the maximum theoretical efficiency and maximum Jsc value that these two EQE curves can reach when combined to set the y limit on the plots
                if i == 0:
                    # We calculate the efficiency of the EQE curve centered at the solar irradiance maximum (635 nm) and then double it to account for the maximum efficiency this EQE curve pari will ever have
                    EQE_Max = REG.Random_generated_EQE_curves(EQE_Top_Hat_curve(Bgap=(635+(EQE_width/2)), EQE_width=EQE_width), Solar_Data)
                    Max_efficiency_value = EQE_Max.Total_Eff *2
                    Max_Jsc_value = EQE_Max.Total_Jsc *2


                if Output_animation:

                    # If we chose to output an animation we need to generate the necessary graphs for each EQE peak separation
                    # In this section we set the necessary graphs
                    gs = gridspec.GridSpec(2, 2)            # Create 2x2 sub plots and then span the third graph onto the lower two subplots

                    fig = plt.figure(figsize=(12, 9))  # We set a big figure size so that we can actually see what is going on
                    fig.suptitle('Two Sliding EQE generated curves compared, width '+str(EQE_width)+' nm', fontsize=16)
                    ax1 = fig.add_subplot(gs[0, 0])  # row 0, col 0
                    ax1.plot(EQE_pair.Dividing_wavelength_list, EQE_pair.Eff_Dividing_wavelength_graph_1, label='EQE 1 Efficiency')  # The first figure is the efficiency vs the dividing wavelength
                    ax1.plot(EQE_pair.Dividing_wavelength_list, EQE_pair.Eff_Dividing_wavelength_graph_2, label='EQE 2 Efficiency')
                    ax1.plot(EQE_pair.Dividing_wavelength_list, EQE_pair.Eff_Dividing_wavelength_graph_total, label='Total Efficiency')
                    ax1.set_title('Efficiency vs Dividing Wavelength')
                    ax1.set_ylim(top= Max_efficiency_value,bottom=0)
                    ax1.legend(loc='center right')
                    ax1.set(xlabel='Dividing Wavelength /nm', ylabel='Efficiency /%')

                    ax2 = fig.add_subplot(gs[0, 1])  # row 0, col 1
                    ax2.plot(EQE_pair.Dividing_wavelength_list, EQE_pair.Jsc_Dividing_wavelength_graph_1, label='EQE 1 Jsc')  # The second thing we plot is the Jsc vs Dividing wavelength
                    ax2.plot(EQE_pair.Dividing_wavelength_list, EQE_pair.Jsc_Dividing_wavelength_graph_2, label='EQE 2 Jsc')
                    ax2.plot(EQE_pair.Dividing_wavelength_list, EQE_pair.Jsc_Dividing_wavelength_graph_total, label='Total Jsc')
                    ax2.set_title('Jsc vs Dividing Wavelength')
                    ax2.legend(loc='center right')
                    ax2.set_ylim(top=Max_Jsc_value,bottom=0)
                    ax2.set(xlabel='Dividing Wavelength /nm', ylabel='Jsc / mA * cm^-2')

                    ax3 = fig.add_subplot(gs[1, :])  # row 1, span all columns
                    ax3.plot(sf.Extract_Column(EQE1.EQE_curve, 0), sf.Extract_Column(EQE1.EQE_curve, 1), label='EQE 1')  # The third thing we plot are the actual EQE curves
                    ax3.plot(sf.Extract_Column(EQE2.EQE_curve, 0), sf.Extract_Column(EQE2.EQE_curve, 1), label='EQE 2')
                    ax3.set_title('EQE values')
                    ax3.legend(loc='upper right')
                    ax3.set(xlabel='Wavelength /nm', ylabel='EQE /%')

                    # Finally we set the figure name with the directory we want to save it to and we save and close all the figures open to continue through the loop
                    fig_name = ' Binary rainbow sliding EQE curve ' + str(Saved_figures) + '.png'
                    fig_name = sf.Full_path_adder(fig_name, Current_width_save_directory)
                    # print(fig_name)
                    plt.savefig(fig_name)
                    plt.close('all')

                    Image_file_list.append(fig_name)                                                        # We append the image full path to the image file list to create the animation afterwards

                # We also want to keep the user informed about the progress of the file conversion so we update the timer at every loop and print an informative message
                Saved_figures += 1  # We update the counter every time we save a figure

                Timer1.Update_progress(Saved_figures, Total_figures,kronos=True,Print_progress=True)  # And we also update the progress value

            if Output_animation:
                # We finally take the image list and create a gif with the specified duration and save it in the current width directory
                with imageio.get_writer(sf.Full_path_adder(('Binary rainbow sliding EQE curves animation '+str(EQE_width)+' nm.gif'),Current_Bgap_save_directory), mode='I', duration=Frame_duration) as writer:
                    for filename in Image_file_list:
                        image = imageio.imread(filename)
                        writer.append_data(image)

                # If we have selected not to save the animation graphs we delete all files within the current width directory as well as the directory itself
                if not Save_animation_graphs:
                    for file in Image_file_list:
                        os.remove(file)
                    os.rmdir(Current_width_save_directory)


        # Finally we plot the enhancement graphs for each EQE width and the ones that have been normalized on a multisubplot and if enabled we save it on a png file
        gs1 = gridspec.GridSpec(2, 1)

        colors = pl.cm.jet(np.linspace(0, 1, Total_width_values))  # We set the color spectrum we will use for the plotting

        fig1 = plt.figure(figsize=(12, 9))                                                                                          # We set a big figure size so that we can actually see what is going on
        plt.subplots_adjust(hspace=0.3)
        fig1.suptitle(('Multiple width EQE curve efficiency enhancement factor analysis with'+str(Reference_Bgap)+' nm Bgap'), fontsize=16)
        ax1 = fig1.add_subplot(gs1[0, 0]) # row 0, col 0                                                                                  # Plot one of the random generated curves
        for k in range(Total_width_values):
            ax1.plot(sf.Extract_Column(EQE_enhancement_list[k],0),sf.Extract_Column(EQE_enhancement_list[k],2),label= ('EQE peak width '+str(round(width_values_list[k]))+' nm'),color = colors[k] )
        ax1.set_title('Efficiency enhancement for two sliding EQE curves')
        ax1.legend(loc='upper left')
        ax1.set_xlim(left=-250)
        ax1.set(xlabel='Peak Wavelength difference /nm', ylabel='Efficiency enhancement factor /x')


        ax2 = fig1.add_subplot(gs1[1, 0]) # row 0, col 0                                                                                  # Plot one of the random generated curves
        for k in range(Total_width_values):
            ax2.plot(sf.Extract_Column(EQE_enhancement_list[k],1),sf.Extract_Column(EQE_enhancement_list[k],2),label=  ('EQE peak width '+str(round(width_values_list[k]))+' nm'),color = colors[k] )
        ax2.set_title('Efficiency enhancement for two sliding EQE curves, normalized')
        ax2.legend(loc='upper left')
        ax2.set(xlabel='Peak Wavelength difference/EQE peak width /nm', ylabel='Efficiency enhancement factor /x')
        ax2.set_xscale('log')
        ax2.set_xlim(left=0.1)  # set the xlim to left, right

        if Save_graphs:
            # Finally we set the figure name with the directory we want to save it to and we save and close all the figures open to continue through the loop
            fig_name = 'Binary rainbow sliding EQE curve enhancement factor per width with '+str(Reference_Bgap)+' nm Bgap.png'
            fig_name = sf.Full_path_adder(fig_name, Current_Bgap_save_directory)
            # print(fig_name)
            plt.savefig(fig_name)

        # Finally we also plot the maximum efficiency graphs for each EQE width and the ones that have been normalized on a multisubplot and if enabled we save it on a png file
        gs2 = gridspec.GridSpec(2, 1)

        fig2 = plt.figure(figsize=(12, 9))  # We set a big figure size so that we can actually see what is going on
        plt.subplots_adjust(hspace=0.3)
        fig2.suptitle('Multiple width EQE curve Total maximum efficiency analysis with'+str(Reference_Bgap)+' nm Bgap', fontsize=16)
        ax1 = fig2.add_subplot(gs2[0, 0])  # row 0, col 0                                                                                  # Plot one of the random generated curves
        for k in range(Total_width_values):
            ax1.plot(sf.Extract_Column(EQE_enhancement_list[k], 0), sf.Extract_Column(EQE_enhancement_list[k], 3), label=('EQE peak width ' + str(round(width_values_list[k])) + ' nm'), color=colors[k],linestyle='-.')
        ax1.set_title('Total maximum efficiency for two sliding EQE curves')
        ax1.legend(loc='upper left')
        ax1.set_xlim(left=-250)
        ax1.set(xlabel='Peak Wavelength difference /nm', ylabel='Total maximum efficiency /%')

        ax2 = fig2.add_subplot(gs2[1, 0])  # row 0, col 0                                                                                  # Plot one of the random generated curves
        for k in range(Total_width_values):
            ax2.plot(sf.Extract_Column(EQE_enhancement_list[k], 1), sf.Extract_Column(EQE_enhancement_list[k], 3), label=('EQE peak width ' + str(round(width_values_list[k])) + ' nm'), color=colors[k],linestyle='-.')
        ax2.set_title('Total maximum efficiency for two sliding EQE curves, normalized')
        ax2.legend(loc='upper right')
        ax2.set(xlabel='Peak Wavelength difference/EQE peak width /nm', ylabel='Total maximum efficiency /%')
        ax2.set_xscale('log')
        ax2.set_xlim(left=0.1)  # set the xlim to left, right


        if Save_graphs:
            # Finally we set the figure name with the directory we want to save it to and we save and close all the figures open to continue through the loop
            fig_name = 'Binary rainbow sliding EQE curve total maximum efficiency per width with '+str(Reference_Bgap)+' nm Bgap.png'
            fig_name = sf.Full_path_adder(fig_name, Current_Bgap_save_directory)
            # print(fig_name)
            plt.savefig(fig_name)

        # plt.show()
        plt.close('all')

