import argparse
import pickle
import pandas as pd
import os, csv
from poss_ing_of import poss_ing_of, sentence_iterator

if __name__ == "__main__":
    # setup command line argument parser
    parser = argparse.ArgumentParser()

    # parser.add_argument("filename", nargs="+")
    # args = parser.parse_args()

    parser.add_argument("directory", help="Directory of the pickle files.")

    args = parser.parse_args()

    filenames = os.listdir(args.directory)
    filenames = map(lambda x: os.path.join(args.directory, x), filenames)

    gerunds = pd.read_csv("match/python/Pattern-2.csv", usecols=["Sentence ID", "Position"])
    csv_output = [['Sentence ID', 'Position', 'Word', 'Gerund Type', 'Sentence']]

    # read pickle files and find poss-ing-of patterns
    for filename in filenames:
        with open(filename, "rb") as file:
            text = pickle.load(file)
        

        for id, sentence in sentence_iterator(text):
            if sentence.skipped:
                continue
            
            rslt_df = gerunds.loc[gerunds['Sentence ID'] == id]
            centers = rslt_df['Position'].tolist()

            for center, kind in poss_ing_of(sentence, centers):
                csv_output.append([id, center, sentence.tokens[center-1], kind, ' '.join(sentence.tokens)])
                print(id, center, sentence.tokens[center-1], kind, ' '.join(sentence.tokens))
    
    with open("Gerunds-0.csv", "w", newline='') as fp:
            writer = csv.writer(fp)
            writer.writerows(csv_output)
