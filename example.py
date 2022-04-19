import argparse
import pickle
import pandas as pd
import os, csv
from poss_ing_of import poss_ing_of, sentence_iterator

from tqdm import tqdm

if __name__ == "__main__":
    # setup command line argument parser
    parser = argparse.ArgumentParser()

    # parser.add_argument("filename", nargs="+")
    # args = parser.parse_args()

    parser.add_argument("directory", help="Directory of the pickle files.")

    args = parser.parse_args()

    filenames = os.listdir(args.directory)
    filenames = map(lambda x: os.path.join(args.directory, x), filenames)

    gerunds = pd.read_csv("updated-updated-updated-matches.csv", usecols=["id", "position", "exclusion"])
    csv_output = [['Recommended Exclusion', 'Sentence ID', 'Position', 'Word', 'Gerund Type', 'Sentence']]

    # read pickle files and find poss-ing-of patterns
    for filename in tqdm(filenames):
        with open(filename, "rb") as file:
            text = pickle.load(file)
        

        for id, sentence in sentence_iterator(text):
            if sentence.skipped:
                continue
            
            rslt_df = gerunds.loc[gerunds['id'] == id]
            centers = rslt_df['position'].tolist()

            for center, kind in poss_ing_of(sentence, [i + 1 for i in centers]):
                excluded = rslt_df.loc[(rslt_df['position'] == center-1), 'exclusion'].item()
                if pd.isna(excluded):
                    excluded = " "
                csv_output.append([excluded, id, center, sentence.tokens[center - 1], kind, ' '.join(sentence.tokens)])
                # print(excluded, id, center, sentence.tokens[center-1], kind, ' '.join(sentence.tokens))
    #TODO: add rule, two other columns to output
    with open("Gerunds-5.csv", "w", newline='') as fp:
            writer = csv.writer(fp)
            writer.writerows(csv_output)
