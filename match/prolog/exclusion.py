from __future__ import annotations

import argparse
import pickle
from pprint import pprint

import pandas as pd


def generate_recommendation(dataframe: pd.DataFrame) -> tuple[bool, str]:
    if len(recommendation := dataframe["Exclude?"].unique()) == 1:
        return True, recommendation[0]

    occurences = dataframe[["Occurrences", "Exclude?"]].values.tolist()
    occurences.sort(key=lambda x: x[0] if x[0] != float("nan") else 0)

    return False, occurences[-1][1]


if __name__ == "__main__":
    # setup command line argument
    parser = argparse.ArgumentParser()

    parser.add_argument("filename", help="File containing the CELEX data.")
    parser.add_argument("-o", "--output", help="File to dump the pickle.")

    args = parser.parse_args()

    # processing CELEX file
    celex = pd.read_csv(args.filename)

    celex["ing"] = celex["Word"].str.lower().str.split().str.get(-1)

    exclusion = {}
    for focus, dataframe in celex.groupby("ing"):
        exclusion[focus] = generate_recommendation(dataframe)

    if args.output:
        with open(args.output, "wb") as file:
            pickle.dump(exclusion, file)
    else:
        pprint(exclusion)
