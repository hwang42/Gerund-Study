from __future__ import annotations

import argparse
import os
import pickle
from typing import Generator

from coca import Sentence, Text
import re
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
        # construct knowledge base
        # print("\n\nSENTENCE", id, ":")

        # clauses, xposes, deprels = convert(sentence)
        clauses = convert(sentence)

        skip_sentence = False
        vbg_present = False
        for node, (text, xpos, head, relation, child) in enumerate(clauses):
            if xpos == "VBG":
                vbg_present = True

                if head != -1:
                    if clauses[head][3] == "amod":
                        skip_sentence = True
                        break

                if child != -1:
                    if clauses[child][3] == "aux":
                        skip_sentence = True
                        break

        if skip_sentence or not vbg_present:
            continue

        # if "amod" in deprels or "aux" in deprels:
        #    continue

        print(sen_id, sentence.dependency.text)


if __name__ == "__main__":

    # setup command line argument parser
    parser = argparse.ArgumentParser()

    parser.add_argument("directory", help="Directory of the pickle files.")

    args = parser.parse_args()

    filenames = os.listdir(args.directory)
    filenames = map(lambda x: os.path.join(args.directory, x), filenames)

    for filename in filter(lambda x: x.endswith(".pkl"), filenames):
        with open(filename, "rb") as storage:
            text = pickle.load(storage)

        detect_pattern1(text)




