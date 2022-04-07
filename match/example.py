import argparse
import pickle

from poss_ing_of import poss_ing_of, sentence_iterator

if __name__ == "__main__":
    # setup command line argument parser
    parser = argparse.ArgumentParser()

    parser.add_argument("filename", nargs="+")

    args = parser.parse_args()

    # read pickle files and find poss-ing-of patterns
    for filename in args.filename:
        with open(filename, "rb") as file:
            text = pickle.load(file)

        for id, sentence in sentence_iterator(text):
            if sentence.skipped:
                continue

            # SOMEHOW FIND ALL THE POSSIBLE GERUND POSITIONS (HAVE DONE BEFORE)
            centers = [i for i, t in enumerate(sentence.tokens, start=1)
                       if t.endswith("ing") or t.endswith("ings")]

            for center, kind in poss_ing_of(sentence, centers):
                print(id, center, kind, ' '.join(sentence.tokens), sep='\t')
