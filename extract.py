from __future__ import annotations

import argparse
import pickle
import sys

import pandas as pd
from tqdm import tqdm

from gerund.filters import gerund_filter
from gerund.structs import sentence_iterator

if __name__ == "__main__":
    # setup command line argument parser
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "exclusion", help="Exclusion recommendation file to be used.")
    parser.add_argument(
        "filename", nargs="+", help="Pickle file(s) of parsed COCA text.")
    parser.add_argument("--output", help="CSV file to write the output.")

    args = parser.parse_args()

    # load exclusion recommendation file, ignore all multi-token entries
    exclusion = pd.read_csv(args.exclusion)
    exclusion = exclusion[-exclusion["Word"].str.contains(" ")]
    exclusion = {i["Word"]: i["Exclude?"] for _, i in exclusion.iterrows()}

    # extract gerund from given pickle files and construct dataframe
    extracted = []

    for filename in tqdm(sorted(args.filename)):
        with open(filename, "rb") as file:
            text = pickle.load(file)

        for id, sentence in sentence_iterator(text):
            if sentence.skipped:
                continue

            for rule, center in gerund_filter(sentence):
                word = sentence.tokens[center - 1]
                excl = exclusion.get(
                    word.lower(), "?") if rule != "VBG" else None
                sent = " ".join(sentence.tokens)

                extracted.append([id, rule, word, center, excl, sent])

    extracted = pd.DataFrame(
        extracted, columns=["id", "rule", "word", "position", "exclusion", "sentence"])

    extracted.to_csv(args.output if args.output else sys.stdout, index=False)
