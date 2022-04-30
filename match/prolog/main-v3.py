from __future__ import annotations

import argparse
import csv
import pickle
import sys

from util import reasoner, sentence_iterator, sentence_search

FIELDS = ["id", "rule", "word", "position",
          "consensus", "exclusion", "sentence"]

reasoner.assertz("string_endswith(String, Suffix) :- "
                 "string_length(String, A), string_length(Suffix, B), "
                 "C is A - B, C >= 0, sub_string(String, C, B, _, Suffix)")

PATTERN = [
    "pattern(1, X) :- xpos(X, 'VBG'), \+ edge(_, X, 'amod'), \+ edge(X, _, 'amod'), \+ edge(X, _, 'aux').",
    "pattern(2, X) :- xpos(X, 'NN'), text(X, S), string_endswith(S, \"ing\").",
    "pattern(3, X) :- xpos(X, 'NNS'), text(X, S), string_endswith(S, \"ings\")."
]

if __name__ == "__main__":
    # setup command line argument parse
    parser = argparse.ArgumentParser()

    parser.add_argument("filename", nargs="+", help="Parse pickle file.")

    args = parser.parse_args()

    # load exclusion dictionary
    with open("./exclusion.pkl", "rb") as file:
        exclusion = pickle.load(file)

    # process each pickle file
    writer = csv.DictWriter(sys.stdout, FIELDS)
    writer.writeheader()

    for filename in sorted(args.filename):
        with open(filename, "rb") as file:
            text = pickle.load(file)

        for id, sentence in sentence_iterator(text):
            answers = sentence_search(sentence, PATTERN, "pattern(X, Y)")

            sent = ' '.join(sentence.tokens)
            for answer in answers:
                row = {"id": id,
                       "consensus": None,
                       "exclusion": None,
                       "sentence": sent}

                row["rule"] = answer["X"]
                row["word"] = sentence.tokens[answer["Y"] - 1]
                row["position"] = answer["Y"] - 1

                if row["rule"] == 2:
                    temp = exclusion.get(row["word"].lower(), (None, None))
                    row["consensus"], row["exclusion"] = temp
                elif row["rule"] == 3:
                    temp = exclusion.get(row["word"][:-1].lower(), (None, None))
                    row["consensus"], row["exclusion"] = temp

                writer.writerow(row)
