--- Classification of Gerund Types ---
This step takes gerunds (their sentence id and position) and categorizes them into:
poss-ing-of, poss-ing, ing-of, det-ing, acc-ing, and vp-ing
It outputs these into a csv that also provides all of the tags for each gerund and the relevant dependencies (immediate edges into/out of the gerund)

--- Run Instructions --- 
in command line (with environment activated), run command "python classify.py [directory of parsed pickle files] [exclusion csv file] [output csv file]"

--- Files Used --- 
example.py
gerund/structs.py

--- Input ---
directory of parsed pickle files, as a command line argument
csv file containing exclusion recommendations, as a command line argument
name of file for csv output to be written to, as a command line argument

--- Output ---
csv file containing dataframe of format:
    ['recommended_exclusion', 'sentence_id', 'position', 'word', 'gerund_type', 'tags', 'dependencies', 'relevant_dependencies', 'sentence']