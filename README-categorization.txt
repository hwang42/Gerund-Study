Categorization of Gerund Types

--- Run Instructions --- 
in command line (with environment activated), run command "python example.py [directory of parsed pickle files]"
*** possibly add matches.csv as a command line argument as well? ***

--- Files Used --- 
example.py
poss_ing_of.py
coca module

--- Input ---
csv file containing exclusion recommendations, currently hardcoded into a readcsv() line (file "updated-updated-updated-matches.csv")
directory of parsed pickle files, as a command line argument

--- Output ---
csv file containing dataframe of format
    ['Recommended Exclusion', 'Sentence ID', 'Position', 'Word', 'Gerund Type', 'Rel_Dep 1 Step', 'Rel_Dep Longest', 'Sentence']