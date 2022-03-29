from __future__ import annotations

import argparse
import os
import pickle
from typing import Generator

from coca import Sentence, Text
import re
import csv
# from pyswip import Prolog

# PATTERN = "pattern(X) :- xpos(X, 'VBG'), \+ dependency(_, X, 'amod'), \+ dependency(X, _, 'aux')"


def flatten(text: Text) -> Generator[tuple[str, Sentence]]:
    for p_index, paragraph in enumerate(text.paragraphs):
        for s_index, sentence in enumerate(paragraph.sentences):
            if not sentence.skipped:
                yield f"{text.text_id[2:]}-{p_index}-{s_index}", sentence


def convert(sentence: Sentence) -> List[list]:
    dependencies = sentence.dependency.to_dict()[0]

    clauses = []
    links = []
    # xposes, deprels  = set(), set()
    for token in dependencies:
        id = token["id"]
        text = token["text"].replace("\"", r'\"')
        xpos = token["xpos"]
        head = token["head"]
        relation = token["deprel"]

        # clauses.append([text, xpos, id, head, relation])
        # xposes.add(xpos)
        # deprels.add(relation)
        clauses.append([text, xpos, head-1, relation, -1])
        links.append([id-1, head-1])

    for link in links:
        if link[1] != -1:
            clauses[link[1]][4] = link[0]  # Update child node

    # return clauses, xposes, deprels
    return clauses


def detect_pattern1(text):
    for id, (sen_id, sentence) in enumerate(flatten(text), start=1):
        clauses = convert(sentence)

        for node, (text, xpos, head, relation, child) in enumerate(clauses):
            if xpos == "VBG":

                if head != -1:
                    if clauses[head][3] == "amod":
                        continue

                if child != -1:
                    if clauses[child][3] == "aux":
                        continue

                print(f"{sen_id}\t{text}\t{node+1}\t{sentence.dependency.text}")
                break


def detect_pattern2(text, exclude_set):
    for id, (sen_id, sentence) in enumerate(flatten(text), start=1):
        clauses = convert(sentence)

        word = ""
        position = 0
        pattern_present = False
        for node, (text, xpos, head, relation, child) in enumerate(clauses):
            if xpos in ("VBG", "NN", "NNS"):
                text = text.lower()
                if re.search(r'\b[a-z]+ings?\b', text):
                    if xpos == "VBG":
                        pattern_present = True

                        if head != -1:
                            if clauses[head][3] == "amod":
                                pattern_present = False

                        if child != -1:
                            if clauses[child][3] == "aux":
                                pattern_present = False

                        if pattern_present:
                            word = text
                            position = node + 1
                            break

                    if xpos == "NN":
                        if text not in exclude_set:
                            pattern_present = True
                            word = text
                            position = node + 1
                            break

                    if xpos == "NNS":
                        if text[:-1] not in exclude_set:
                            pattern_present = True
                            word = text
                            position = node + 1
                            break

        if pattern_present:
            print(f"{sen_id}\t{word}\t{position}\t{sentence.dependency.text}")


if __name__ == "__main__":

    # setup command line argument parser
    parser = argparse.ArgumentParser()

    parser.add_argument("directory", help="Directory of the pickle files.")

    args = parser.parse_args()

    filenames = os.listdir(args.directory)
    filenames = map(lambda x: os.path.join(args.directory, x), filenames)

    # Reading exclude set for pattern 2
    with open('celex-ing.csv', 'r') as fp:
        reader = csv.reader(fp)
        constrains = list(reader)[1:]

    exclude_set = set(x[0].lower() for x in constrains if x[1] == "Y")
    # print(len(exclude_set))
    # print(exclude_set)

    for filename in filter(lambda x: x.endswith(".pkl"), filenames):
        with open(filename, "rb") as storage:
            text = pickle.load(storage)

        # detect_pattern1(text)
        detect_pattern2(text, exclude_set)
