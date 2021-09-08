
# ------------------------------------- This script main function is to find items within lists. The different functions within this script find items with different criteria
# ------------------------------------- The suggested import method for this script is the following: import List_Finder as lstf

# Function that finds an exact match of an item within a 2d list and returns the index where that item is (note it only returns the first dimension index not the second). That is, if the function finds
# the item somewhere within the list_where_to_find[3] sublist it will return a 3 indicating that the item is within that sublist
def in_list(to_find_item, list_where_to_find):                                                          # The function takes the item to find within the list and a 2D list where the item is to be found
    for i, sublist in enumerate(list_where_to_find):                                                    # Enumerates the list, hence it adds an index to the already existing list that will be returned if a match is found. This could also be done with an increasing variable
        if to_find_item in sublist:                                                                     # If the item is found in the sublist, the nested list, it returns the index and stops the function
            return i
    return -1                                                                                           # If the to_find_item is not found it returns -1

# Function that searches within the selected column of a nested 2D list and finds the closest value to a specified one, returning the index where that value resides within the list
# It also uses a tolerance value that can be set so that the closest found item has to be at least a tolerance value apart from the selected value to find. It is set by default as 999 but can be specified to be any value
def find_closest(Value_to_find,list_where_to_find,column_to_search = 0,max_tolerance = 999):            # The function takes the Value that we want to find within the list, the 2D list where to look for and two optional arguments, the column of the 2D list where to search for and the maximum tolerance value
    tolerance = max_tolerance                                                                           # We set the max_tolerance to a high default to make sure there is a match, however if the user decides that @e needs a lower max_tolerance it can be changed.
    index = 0                                                                                           # The lower the max_tolerance the least likely to find a match but the more accurate this match will be

    # We now run through the whole list looking for the closest value to the Value_to_find, only comparing the value with the sublist[column_to_search] item.
    for i, sublist in enumerate(list_where_to_find):
        # print(str(sublist[column_to_search])+'   '+str(to_find_item)+'  difference = ' +str(abs(sublist[column_to_search]-to_find_item)) +'  Tolerance = ' + str(tolerance))   # print For debugging purposes

        # If the current tolerance value is higher than the absolute difference between the item to find and the sublist[column_to_search] item we have a new closest candidate
        if tolerance > abs(sublist[column_to_search] - Value_to_find):
            tolerance = abs(sublist[column_to_search] - Value_to_find)                                   # We store the difference of this new candidate as the new tolerance to search only for tolerances lower than the current one
            index = i                                                                                    # We set the index to the current value to store the location of the current match. In case a new, better match is found the index will be automatically updated to that value's index

    # If the found tolerance were to be equal or bigger (it should never be able to be bigger but just in case) than the max tolerance value
    # We will return a -1 indicating there is no match within the set tolerance
    if tolerance >= max_tolerance:
        return -1
    # If that condition is not fulfilled we will return the index of the closest match because it means we have found a match
    return index
