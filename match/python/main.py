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
TEST_PATTERN = 2    # 1 or 2


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
        clauses.append([text, xpos, head - 1, relation, -1])
        links.append([id - 1, head - 1])

    for link in links:
        if link[1] != -1:
            clauses[link[1]][4] = link[0]  # Update child node

    # return clauses, xposes, deprels
    return clauses


def detect_pattern1(text):
    # csv_output = [['Sentence ID', 'Word', 'Position', 'Sentence']]
    pattern_list = []
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

                # print(f"{sen_id}\t{text}\t{node+1}\t{sentence.dependency.text}")
                pattern_list.append([sen_id, text, str(node + 1), sentence.dependency.text])
    return pattern_list

# TODO: Gerund Type, Relevant Dependencies

def detect_pattern2(text, exclude_set, dilemma_set):
    # csv_output = [['Sentence ID', 'Match Pattern', 'Word', 'Position', 'Sentence']]
    # dilemma_words = [['Sentence ID', 'Match Pattern', 'Word', 'Position', 'Sentence']]
    pattern_list = []
    dilemma_list = []

    for id, (sen_id, sentence) in enumerate(flatten(text), start=1):
        clauses = convert(sentence)

        patt_id = 0
        for node, (text, xpos, head, relation, child) in enumerate(clauses):
            if xpos in ("VBG", "NN", "NNS"):
                text = text.lower()
                if re.search(r'\b[a-z]+ings?\b', text):
                    pattern_present = False
                    if xpos == "VBG":
                        pattern_present = True

                        if head != -1:
                            if clauses[head][3] == "amod":
                                pattern_present = False

                        if child != -1:
                            if clauses[child][3] == "aux":
                                pattern_present = False

                        if pattern_present:
                            patt_id = 1

                    elif xpos in ("NN", "NNS"):
                        if xpos == "NN":
                            patt_id = 2
                            set_text = text
                        else:
                            patt_id = 3
                            set_text = text[:-1]

                        if set_text in exclude_set:
                            pattern_present = False
                            multiwords = exclude_set[set_text]
                            # Check if multiple words are present in patterns to check them all
                            if multiwords[0] != -1:
                                start_node = node - multiwords[0]
                                for i, node_id in enumerate(range(start_node, start_node + len(multiwords[1]))):
                                    if multiwords[i] != clauses[node_id][0]:
                                        pattern_present = True
                                        break
                        else:
                            pattern_present = True

                        in_dilemma = False
                        if set_text in dilemma_set:
                            in_dilemma = True
                            multiwords = dilemma_set[set_text]
                            if multiwords[0] != -1:
                                start_node = node - multiwords[0]
                                # Check if multiple words are present in patterns to check them all
                                for i, node_id in enumerate(range(start_node, start_node + len(multiwords[1]))):
                                    if multiwords[i] != clauses[node_id][0]:
                                        in_dilemma = False
                                        break
                        if in_dilemma:
                            dilemma_list.append([sen_id, str(patt_id), text, str(node+1), sentence.dependency.text])

                    if pattern_present:
                        # print(f"{sen_id}\t{patt_id}\t{text}\t{node + 1}\t{sentence.dependency.text}")
                        pattern_list.append([sen_id, str(patt_id), text, str(node+1), sentence.dependency.text])

    return pattern_list, dilemma_list


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

    if TEST_PATTERN == 1:
        print("Parsing Pattern 1. . .")
        csv_output = [['Sentence ID', 'Word', 'Position', 'Sentence']]

        for filename in filter(lambda x: x.endswith(".pkl"), filenames):
            with open(filename, "rb") as storage:
                text = pickle.load(storage)

            csv_output += detect_pattern1(text)

        with open("Pattern-1.csv", "w", newline='') as fp:
            writer = csv.writer(fp)
            writer.writerows(csv_output)

        print("Parsing completed & the csv file is saved to disk. . .")

    elif TEST_PATTERN == 2:
        print("Parsing Pattern 2. . .")

        # Creation of exclude and dilemma set
        exclude_set = {}
        dilemma_set = {}
        for x in constrains:
            x[0] = x[0].lower()
            # 1st index will store position of -ing(s) in multi-words; 2nd index stores all words if > 1
            str_pos = [-1, []]

            if '-' in x[0]:
                for pos, word in enumerate(x[0].split('-')):
                    if str_pos[0] == -1:
                        if re.search(r'[a-z]+ings?', word):
                            str_pos[0] = pos
                    str_pos[1].append(word)

            if x[1] == "Y":
                exclude_set[x[0]] = str_pos
            if x[1] == "?":
                dilemma_set[x[0]] = str_pos

        csv_output = [['Sentence ID', 'Match Pattern', 'Word', 'Position', 'Sentence']]
        dilemma_words = [['Sentence ID', 'Match Pattern', 'Word', 'Position', 'Sentence']]

        for filename in filter(lambda x: x.endswith(".pkl"), filenames):
            with open(filename, "rb") as storage:
                text = pickle.load(storage)

            pat, dil = detect_pattern2(text, exclude_set, dilemma_set)

            csv_output += pat
            dilemma_words += dil

        with open("Pattern-2.csv", "w", newline='') as fp:
            writer = csv.writer(fp)
            writer.writerows(csv_output)

        with open("Dilemma_Words.csv", "w", newline='') as fp:
            writer = csv.writer(fp)
            writer.writerows(dilemma_words)

        print("Parsing completed & the csv files are saved to disk. . .")
