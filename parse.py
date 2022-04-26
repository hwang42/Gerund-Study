from __future__ import annotations

import argparse
import os.path
import pickle

from tqdm import tqdm

from coca import text_from_tokens
from gerund.structs import load_coca

if __name__ == "__main__":
    # setup command line argument parser
    parser = argparse.ArgumentParser()

    parser.add_argument("filename", help="File containing the COCA corpus.")
    parser.add_argument("--directory", default=".")

    args = parser.parse_args()

    # parse COCA corpus and store results
    with open(args.filename, "r") as file:
        for line in tqdm(file):
            if not line.startswith("##"):
                continue

        text = text_from_tokens(line.split())
        filename = os.path.join(args.directory, text.text_id[2:] + ".pkl")

        with open(filename, "wb") as file:
            pickle.dump(text, file)
