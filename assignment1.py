####
## NLP Assignment 1
## Author: James Imgrund
## Description: read many datafiles of text and search for acronyms and their meanings.
##   Record the acronyms, meanings, and which files they reside in and
##   record this data into a csv file


from nltk.tokenize import TreebankWordTokenizer
treebank_tokenizer = TreebankWordTokenizer()

import re
import os

from os import listdir
from os.path import isfile, join

# all data to be processed must reside within this directory structure.
# the csv output datafile will be placed within a subdirectory of this.
# the subdirectory will be "output" and the csv file will be named "acronyms.csv"
data_directory = "/Users/jimgrund/Documents/GWU/NLP/assignment1/data"


# an acronym will be any string of chars that contains only
# upper case letters and zero or one lower case letters
# the lower case letter can not be the first or last letter of the string
acronym_regex = re.compile('^[A-Z]+[a-z]?[A-Z]+$')


# construct an object for handling the Acronym details
class Acronym:
    def __init__(self, acronym, definition, locations):
        self.acronym = acronym
        self.definition = definition
        self.locations = locations

    def to_csv(self):
        tup = self.acronym, self.definition, "|".join(map(str,self.locations))
        return(",".join( tup ))


# we'll store the acronym objects in a dict for easy/quick lookups
# this will be a dict of Acronym objects
acronyms = dict()

# initialize a counter to track how many acronyms we get definitions for
match_counter = 0

# ensure we're in the directory with the data files
os.chdir(data_directory)

# loop across every file within the data directory
for file_name in listdir(data_directory):
    # test/verify that the file found is a file and not a directory or other object
    if isfile(join(data_directory, file_name)):

        #print("- ", file_name)

        # open the file for reading
        file_handle = open(file_name, "r")

        # read all data from file into file_data variable
        file_data = file_handle.read()

        # tokenize the data read from the file so we have every word of the file in a toke for analysis
        tokens = treebank_tokenizer.tokenize(file_data)
        # print(tokens)

        # initialize an index itentifier so we can track which token in the file we're working with
        token_index = 0

        # loop across all tokens in the file
        for token in list(tokens):

            # test to see if the current token matches the regex that defines what an acronym looks like
            acronym_match = acronym_regex.match(token)

            # if we found what appears to be an acronym, then process it accordingly
            if acronym_match:

                # just for sanity sake, let's call the current token "acronym"
                acronym = token

                # record the number of chars within this acronym
                acronym_length = len(acronym)

                # print('Acronym found at index ', token_index, ' with length ', acronym_length, ': ', match.group())

                # initialize the definition of the acronym to blank
                acronym_definition = ''

                # initalize match to False and only reset it to True if we match potential definition tokens
                match = False

                # initialize a counter to track how many letters of the acronym
                acronym_letter_counter = 0

                # loop across the previous tokens for the number of characters in the acronym.
                # if the acronym consisted of 4 letters, then process the previous 4 tokens.
                # we subtract an extra 1 because the token immediately prior to the
                # acronym is assumed to always be a parens
                for iterator in range(token_index - acronym_length - 1, token_index - 1):
                    # print(tokens[iterator])

                    # verify the first letter of the previous tokens match the acronym letters
                    if (tokens[iterator][0].lower() == acronym[acronym_letter_counter].lower()):
                        # we found a match so record the token into acronym_definition
                        acronym_definition += " " + tokens[iterator]
                        match = True
                    else:
                        # we didn't find a match so immediately break out
                        # and move on to find the next acronym.  no definition for this current acronym
                        match = False
                        # print('False match')
                        break

                    acronym_letter_counter += 1

                if match:
                    # if we got here, then we successfully found a definition for all letters of the acronym
                    # print('Possible meaning of acronym: ', acronym_definition)

                    # store the definition into a dictionary of acronyms
                    acronyms[acronym] = Acronym(acronym, acronym_definition, [file_name])
                    match_counter += 1
                    # acronyms_list.append(Acronym(acronym,acronym_definition,[file_name]))
                else:
                    # no definition has been found, store the file location
                    # of this instance of the acronym in the dictionary
                    if acronyms.get(acronym):
                        # acronym already exists in dictionary, update the listing of file locations
                        # print("found acronym in the dict: ",acronym)
                        if file_name not in acronyms[acronym].locations:
                            acronyms[acronym].locations.append(file_name)
                            # print("filename not found, appending filename: ", acronym, " || ", file_name)

                    else:
                        # acronym wasn't found in the dictionary, create a new entry for this file location
                        acronyms[acronym] = Acronym(acronym, "", [file_name])
                        # print("defined acronym without meaning and with filename: ", acronym, " || ", file_name)


            # move on to the next token in the overall file
            token_index += 1


print("total acronyms with definitions: ", match_counter)
print("total acronyms: ", len(acronyms))


# verify we have an output directory to dump the acronym data
if not os.path.isdir("output"):
    # output dir didn't exist, let's create it
    os.makedirs("output")

# create (or overwrite) the acronyms.csv file within the output directory
# and setup a filehandle for writing to
acronyms_fh = open("output/acronyms.csv", "w")

# for every acronym in the acronyms dictionary, loop
for item in sorted(acronyms.keys()):
    # write a csv entry of the current dict element to the filehandle
    acronyms_fh.write(acronyms[item].to_csv() + "\n")
    #print('key: ', item)
    #print('csv: ', acronyms[item].to_csv())


# close the acronyms filehandle
acronyms_fh.close()
