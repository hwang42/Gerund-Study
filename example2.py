import argparse
import pickle
import pandas as pd
import os

from poss_ing_of import poss_ing_of, sentence_iterator

if __name__ == "__main__":
    # setup command line argument parser
    parser = argparse.ArgumentParser()

    parser.add_argument("directory", help="Directory of the pickle files.")
    
    args = parser.parse_args()

    gerunds = pd.read_csv("match/python/Pattern-2.csv", usecols=["Sentence ID", "Position"])
    # read pickle files and find poss-ing-of patterns
    for filename in args.filename:
        with open(filename, "rb") as file:
            text = pickle.load(file)

        for id, sentence in sentence_iterator(text):
            if sentence.skipped:
                continue
            
            rslt_df = gerunds.loc[gerunds['Sentence ID'] == id]
            centers = rslt_df['Positions']
            # SOMEHOW FIND ALL THE POSSIBLE GERUND POSITIONS (HAVE DONE BEFORE)
            # centers = [i for i, t in enumerate(sentence.tokens, start=1)
            #            if t.endswith("ing") or t.endswith("ings")]

            for center, kind in poss_ing_of(sentence, centers):
                print(id, center, kind, ' '.join(sentence.tokens), sep='\t')

    

    # for index, row in gerunds.iterrows():
    #     filename = row["Sentence ID"] + ".pkl"
    #     filename = os.path.join(args.directory, filename)
    #     # filename = str(args.filename) + row["Sentence ID"] + ".pkl"
    #     with open(filename, "rb") as file:
    #         text = pickle.load(file)
    #         print(text)
    #     for id, sentence in sentence_iterator(text):
    #         if sentence.skipped:
    #             continue

    #         for center, kind in poss_ing_of(sentence, list(row["Position"])):
    #             print(id, center, kind, ' '.join(sentence.tokens), sep='\t')
