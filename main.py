import argparse
import pickle

from coca import text_from_tokens

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("filename")

    args = parser.parse_args()

    with open(args.filename, "r") as file:
        for line in filter(lambda x: x.startswith("##"), file):
            text = text_from_tokens(line.strip().split())

            with open(text.text_id[2:] + ".pkl", "wb") as storage:
                pickle.dump(text, storage)
