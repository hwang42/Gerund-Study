import argparse
import pickle
import pandas as pd
import os, csv
from poss_ing_of import poss_ing_of, sentence_iterator
from window import window, longest_dep

from tqdm import tqdm

if __name__ == "__main__":
    
    # takes one command line argument: directory of pickle files that contain the dependency parses
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Directory of the pickle files.")
    args = parser.parse_args()

    filenames = os.listdir(args.directory)
    # create list of complete paths of all files in the directory
    filenames = [os.path.join(args.directory, x) for x in filenames]
    # read sentence_id, word position, and exclusion result from pattern-matching output csv
    gerunds = pd.read_csv("updated-updated-updated-matches.csv", usecols=["id", "position", "exclusion"])
    # create structure of final csv output with annotated gerund type added, and relevant dependencies
    csv_output = [['Recommended Exclusion', 'Sentence ID', 'Position', 'Word', 'Gerund Type', 'Rel_Dep 1 Step', 'Rel_Dep Longest', 'Sentence']]

    # iterate and load each pickle file
    for filename in tqdm(filenames):
        with open(filename, "rb") as file:
            text = pickle.load(file)
        
        # iterate through all sentences in that pickle file
        for id, sentence in sentence_iterator(text):
            if sentence.skipped:
                continue
            
            # find all gerunds that have that sentence_id, and store in rslt_df dataframe
            rslt_df = gerunds.loc[gerunds['id'] == id]
            # extract all centers (indices of gerunds) from that sentence
            centers = rslt_df['position'].tolist()

            # for each center and its categorization (all centers+=1 because we switch from 0- to 1-indexed)
            for center, kind in poss_ing_of(sentence, [i + 1 for i in centers]):
                # store excluded results
                excluded = rslt_df.loc[(rslt_df['position'] == center-1), 'exclusion'].item()
                # change from Na to a space
                if pd.isna(excluded):
                    excluded = " "
                rel_dep1 = window(sentence, center)
                rel_dep2 = longest_dep(sentence, center)
                # add this gerund data to the output csv
                csv_output.append([excluded, id, center, sentence.tokens[center - 1], kind, rel_dep1, rel_dep2, ' '.join(sentence.tokens)])

    #TODO: add rule, two other columns to output
    # write the full output to a csv file
    with open("Gerunds-5.csv", "w", newline='') as fp:
            writer = csv.writer(fp)
            writer.writerows(csv_output)
