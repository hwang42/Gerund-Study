--- Gerund Extraction ---
this step takes a file with a list of gerunds or -ing words to exclude, and marks the dataset with whether or not a word is excluded, and why.
this output can either be written to a csv file or printed to stdout.

--- Run Instructions --- 
in command line (with environment activated), run command "python extract.py [exclusion recommendation file] [parsed pickle files] --output [csv output file]"

--- Files Used --- 
extract.py
gerund/filters.py
gerund/struct.py

--- Input ---
csv file of recommended exclusions
list of parsed pickle files (can be written as [containing directory]/* if you want all files in a folder)
optional: name of the csv output file

--- Output ---
if --output filename is given, csv file containing dataframe of exclusion recommendations
    ["id", "rule", "word", "position", "exclusion", "sentence"]
if no output file given, the dataframe is printed to stdout