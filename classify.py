import argparse
import pickle
import pandas as pd
import os, csv
from gerund.structs import sentence_iterator, classify_gerunds
from window import window

from tqdm import tqdm

if __name__ == "__main__":

    # takes three command line arguments: directory of pickle files that contain the dependency parses, exclusion file, and output file
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Directory of the pickle files.")
    parser.add_argument("exclusions", help="csv exclusion file")
    parser.add_argument("output", help="csv output file")
    args = parser.parse_args()

    filenames = os.listdir(args.directory)
    # create list of complete paths of all files in the directory
    filenames = [os.path.join(args.directory, x) for x in filenames]
    # read sentence_id, word position, and exclusion result from exclusion csv
    gerunds = pd.read_csv(args.exclusions, usecols=["id", "position", "exclusion"])
    # create structure of final csv output with annotated gerund type added, tags and relevant dependencies
    csv_output = [['recommended_exclusion', 'sentence_id', 'position', 'word', 'gerund_type', 'tags', 'dependencies',
                   'relevant_dependencies', 'sentence']]

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

            # for each center (1-indexed) and its categorization
            for center, kind in classify_gerunds(sentence, centers):
                # store excluded results
                excluded = rslt_df.loc[(rslt_df['position'] == center), 'exclusion'].item()
                #skip over any gerunds that should be excluded
                if excluded == "Y" or excluded == "R":
                    continue
                # change from Na to a space
                if pd.isna(excluded):
                    excluded = " "
                tags, all_dep, rel_dep = window(sentence, center)
                # add this gerund data to the output csv
                csv_output.append([excluded, id, center, sentence.tokens[center-1], kind, tags, all_dep, rel_dep,
                                   ' '.join(sentence.tokens)])

    # TODO: add rule, two other columns to output
    # write the full output to a csv file
    with open(args.output, "w", newline='') as fp:
        writer = csv.writer(fp)
        writer.writerows(csv_output)