
#------------- This script contains functions mainly regarding text Importing from txt files to python 2D lists --------------------------------------------------------------------
#------------- It features header data extraction and large file compatibility, returning all the data as a 2D list of floats ------------------------------------------------------
#------------- We recommend to import this script in the following manner: import Text_Importer as txtImp --------------------------------------------------------------------------

import sys                                                                  # Import all necessary libraries and secondary files with functions
import csv

# Prefunction that sets the file size that the csv module can handle as high as possible
Maximum_file_size = sys.maxsize                                             # First we set the maximum file size as the systems maximum allowed size

# Loop that lowers the Maximum file size by a factor of 10 as long as the OverflowError occurs
while True:                                                                 # Loop that keeps ongoing until it is broken
    try:
        csv.field_size_limit(Maximum_file_size)                             # Try to set the field_size_limit to the current Maximum_file_size
        break                                                               # If no error is detected on the previous step, this will break the loop and we will continue to the rest of the code
    except OverflowError:                                                   # If we get an OverflowError
        Maximum_file_size = int(Maximum_file_size/10)                       # We lower the Maximum_file_size by a factor of 10 and try again until the error no longer appears


# Function that takes a txt, csv or any file with established separation, with a grid like structure and converts it to a 2D list containing the same amount of columns and rows.

def import_txt(File_Path,Ignore_Header = True,delimiter = '\t', Replace_Characters = ['"',"'",'[',']']):            # The function takes a File_Path variable with the file location, and two optional arguments that set if it will ignore the header (it will by default) and which will be the delimeiter (a tab by defaul)
    with open(File_Path) as TXT_file:                                       # Recommended to use with when opening files to prevent corruption in case of sudden close as opposed to Open File_Path as a csv file which can lead to corruption
        Raw_Data = csv.reader(TXT_file, delimiter=delimiter)                # We import the file using the csv.reader command and we store it on the Raw_Data variable

        List_2D = list()                                                    # We initialize the list that will contain all the
        Header_information = list()                                         # We initialize the list that will contain the Header info even if the Ignore header is True
        Header_Ignored_or_read = False                                      # Fe initialize a variable that will tell us if the Header has been read or not

        # This for loop will go through the Raw_Data, extracting and organizing all the extracted columns and rows into the 2D list
        for Data_row in Raw_Data:                                           # For each data row we find
            if not Ignore_Header and not Header_Ignored_or_read:            # We first discard the headers. If needed they can be extracted and returned as well. It is only done on the first loop when the Header_Ignored_or_read is False
                for Column in Data_row:                                     # For each column we find
                    Column = repr(Column)                                   # We first convert the Column data to a string
                    for Replace_Character in Replace_Characters:            # For each replace character we have
                        Column = Column.replace(Replace_Character,'')       # We try to replace it from the header
                    try:
                        Column = float(Column)                              # We try to convert the header data to floats
                        Header_information.append(Column)                   # If we succeed on converting them to numbers we append them to the Header_in
                    except Exception as e:
                        #print('Header information is not numerical')       # Print an error for debugging purposes
                        Header_information = Data_row                       # If at least one of the headers is not numerical we set the Header_information as the entire Data_row that contains the header
                        break                                               # and we break the for loop to prevent any more conversion of the header data to floats

            # Now we loop trough the actual data rows converting them to a list of floats only if the header data has already been either processed or ignored
            if Header_Ignored_or_read:
                Columns = list()                                            # We initialize a value that will hold all the different columns data together before appending it as a full row
                for Column in Data_row:                                     # For each column within the Current Data_Row
                    Column = repr(Column)                                   # We first convert the Column data to a string
                    for Replace_Character in Replace_Characters:            # For each replace character we have
                        Column = Column.replace(Replace_Character, '')      # We try to replace each character from the data to ease the conversion to float
                    Column = float(Column)                                  # Once all the characters have been replaced we convert our data to a float
                    Columns.append(Column)                                  # We append the current column item to the Columns variable which holds the full row of values
                List_2D.append(Columns)                                     # We append the Columns variable, containing the full row of data to the List_2D variable to add the values as rows within the list

            Header_Ignored_or_read = True                                   # We set Header_Ignored_or_read as True on the first loop to allow the numerical data reading on the next loops
        if Ignore_Header:
            return List_2D                                                  # When the for loop finishes, if we chose to ignore the header, only a 2D list will be returned
        else:
            return List_2D,Header_information                               # On the contrary, if when the for loop finishes we chose NOT to ignore the header, we return a tuple with the List_2D and the Header_information


# ------------------------------------------------------------------------------ txtImp tester program, uncomment if you want to debug this script: ---------------------------------------------------------------------------------------------------
#
# import Text_Importer as txtImp
# from tkinter import filedialog
# import os
#
# if __name__ == '__main__':
#     EQE_TXT_1 = filedialog.askopenfilename(title='Select the EQE TXT you want to analyze',initialdir=os.getcwd(), filetypes=(('txt files','*.txt'),('All files','*.*')))        # Prompt the user to open a file that contains the EQE txt files, and assign the file path to the variable EQE_TXT_1
#     EQE_Data_1 = txtImp.import_txt(EQE_TXT_1,True)                          # Import the EQE data into the EQE_Data_1 Variable without header info
#     print(*EQE_Data_1, sep='\n')                                            # For debugging purposes
#
#     EQE_TXT_2 = filedialog.askopenfilename(title='Select the EQE TXT you want to analyze',initialdir=os.getcwd(), filetypes=(('txt files','*.txt'),('All files','*.*')))        # Prompt the user to open a file that contains the EQE txt files, and assign the file path to the variable EQE_TXT_1
#     EQE_Data_2,Header = txtImp.import_txt(EQE_TXT_2,False)                  # Import the EQE data into the EQE_Data Variable but this time with the header info as well
#     print(*EQE_Data_2, sep='\n')                                            # For debugging purposes
#     print(Header)
#

########################################################---------------------------------------------- Uncomment until here to test the script ---------------------------------------------------############################################################################################


# Old deprecated functions ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#
# def import_txt_Solar(File_to_import):                                   # Function to import a TXT file (specially useful for the solar curve txt) and return it in the form of a list
#     with open(File_to_import) as csv_file:                              # Recommended to use with when opening files to prevent corruption in case of sudden close. Open File_to_import as a csv file
#         csv_reader = csv.reader(csv_file, delimiter='\t')               # Import the file into a set
#         line_count = 0                                                  # Initialize the line_count
#         for row in csv_reader:                                          # For each row in the set :
#             if line_count == 0:                                         # We first discard the headers. If needed they can be extracted and returned as well
#                 #print(f'Column names are: {", ".join(row)}')           # Debugging purposes
#                 line_count += 1                                         # We increase the line count to jump to the next step on the next iteration
#             elif line_count == 1:                                       # When we are in the first data row
#                 item1 = float(repr(row[0]).replace("'",""))             # We store the first two values within the temporal variables item1 and item2 as float variables so that they can be operated as numbers afterwards
#                 item2 = float(repr(row[1]).replace("'",""))             # We also have to replace the single quotes (') to prevent the conversion failure to float
#                 ##print(f'{row[0]},{row[1]},{row[2]}')                  # Print For debugging purposes
#                 Variable_for_data = list([[item1,item2]])               # We initialize a 2 dimensional list with the first items
#                 line_count += 1                                         # We increase the line count to jump to the next step on the next iteration
#             else :                                                      # When we are in the second or later data rows
#                 item1 = float(repr(row[0]).replace("'",""))             # We store the current row first two values within the temporal variables item1 and item2 as float variables so that they can be operated as numbers afterwards
#                 item2 = float(repr(row[1]).replace("'",""))             # We still have to replace the single quotes (') to prevent the conversion failure to float
#                 Variable_for_data.append([item1,item2])                 # We append the current items to the already existing 2 dimensional list to add the values as rows within the list
#                 ##print(temp_array)                                     # Print For debugging purposes
#                 line_count += 1                                         # We increase the line count even though it is not really necessary
#         #print(f'Processed {line_count} lines.')                        # Print For debugging purposes
#         #print(temp_array)                                              # Print For debugging purposes
#         #print(temp_array.shape)                                        # Print For debugging purposes
#         #print(*Variable_for_data, sep='\n')                            # Print For debugging purposes
#         return Variable_for_data                                        # When the for loop finishes we return the created list
#
# def import_txt_EQE(File_to_import):                                     # Function to import a TXT file (specially useful for the EQE curve txt) and return it in the form of a list
#     with open(File_to_import) as csv_file:                              # Recommended to use with when opening files to prevent corruption in case of sudden close. Open File_to_import as a csv file
#         csv_reader = csv.reader(csv_file, delimiter='\t')               # Import the file into a set
#         line_count = 0                                                  # Initialize the line_count
#         for row in csv_reader:                                          # For each row in the set :
#             if line_count == 0:                                         # We first discard the headers. If needed they can be extracted and returned as well
#                 #print(f'Column names are: {", ".join(row)}')           # Print For debugging purposes
#                 line_count += 1                                         # We increase the line count to jump to the next step on the next iteration
#             elif line_count == 1:                                       # When we are in the first data row
#                 ##print(f'{row[0]},{row[1]},{row[2]}')                  # Print For debugging purposes
#                 item1 = float(repr(row[0]).replace("'",""))             # We store the first three values within the temporal variables item1, item2 and item3 as float variables so that they can be operated as numbers afterwards
#                 item2 = float(repr(row[1]).replace("'",""))             # We also have to replace the single quotes (') to prevent the conversion failure to float
#                 item3 = float(repr(row[2]).replace("'",""))
#                 Variable_for_data = list([[item1,item2,item3]])         # We initialize a 2 dimensional list with the first items
#                 line_count += 1                                         # We increase the line count to jump to the next step on the next iteration
#             else :                                                      # When we are in the second or later data rows
#                 item1 = float(repr(row[0]).replace("'",""))             # We store the current row first three values within the temporal variables item1, item2 and item3 as float variables so that they can be operated as numbers afterwards
#                 item2 = float(repr(row[1]).replace("'",""))             # We still have to replace the single quotes (') to prevent the conversion failure to float
#                 item3 = float(repr(row[2]).replace("'",""))
#                 Variable_for_data.append([item1,item2,item3])           # We append the current items to the already existing 2 dimensional list to add the values as rows within the list
#                 ##print(temp_array)                                     # Print For debugging purposes
#                 line_count += 1                                         # We increase the line count even though it is not really necessary
#         #print(f'Processed {line_count} lines.')                        # Print For debugging purposes
#         #print(temp_array)                                              # Print For debugging purposes
#         #print(temp_array.shape)                                        # Print For debugging purposes
#         #print(*Variable_for_data, sep='\n')                            # Print For debugging purposes
#         return Variable_for_data                                        # When the for loop finishes we return the created list
#
#
