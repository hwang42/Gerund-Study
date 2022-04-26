--- Categorization of Gerund Types ---
This step takes gerunds (their sentence id and position) and categorizes them into:
poss-ing-of, poss-ing, ing-of, det-ing, acc-ing, and vp-ing
It outputs these into a csv that also provides all of the tags for each gerund and the relevant dependencies (immediate edges into/out of the gerund)

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
    ['Recommended Exclusion', 'Sentence ID', 'Position', 'Word', 'Gerund Type', 'Tags', 'Dependencies', 'Relevant Dependencies', 'Sentence']