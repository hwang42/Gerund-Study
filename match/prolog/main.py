from __future__ import annotations

import argparse
import os
import pickle
from typing import Generator

from coca import Sentence, Text
from pyswip import Prolog

PATTERN = "pattern(X) :- xpos(X, 'VBG'), \+ dependency(_, X, 'amod'), \+ dependency(X, _, 'aux')"


def flatten(text: Text) -> Generator[tuple[str, Sentence]]:
    for p_index, paragraph in enumerate(text.paragraphs):
        for s_index, sentence in enumerate(paragraph.sentences):
            if not sentence.skipped:
                yield f"{text.text_id[2:]}-{p_index}-{s_index}", sentence


def convert(sentence: Sentence) -> list[str]:
    dependencies = sentence.dependency.to_dict()[0]

    clauses = []
    for token in dependencies:
        id = token["id"]
        text = token["text"].replace("\"", r'\"')
        xpos = token["xpos"]
        head = token["head"]
        relation = token["deprel"]

        text_clause = f"text({id}, \"{text}\")."
        xpos_clause = f"xpos({id}, '{xpos}')."
        relation_caluse = f"dependency({head}, {id}, '{relation}')."

        clauses.extend([text_clause, xpos_clause, relation_caluse])

    return sorted(clauses)  # sorting is required due to Prolog...


if __name__ == "__main__":
    # setup command line argument parser
    parser = argparse.ArgumentParser()

    parser.add_argument("directory", help="Directory of the pickle files.")

    args = parser.parse_args()

    # process each pickle file
    prolog = Prolog()
    prolog.assertz(PATTERN)

    filenames = os.listdir(args.directory)
    filenames = map(lambda x: os.path.join(args.directory, x), filenames)

    for filename in filter(lambda x: x.endswith(".pkl"), filenames):
        with open(filename, "rb") as storage:
            text = pickle.load(storage)

        for id, sentence in flatten(text):
            # construct knowledge base
            for clause in convert(sentence):
                prolog.assertz(clause[:-1])  # no period for pyswip

            answers = list(prolog.query("pattern(X)"))

            # reset knowledge base
            prolog.retractall("text(_, _)")
            prolog.retractall("xpos(_, _)")
            prolog.retractall("dependency(_, _, _)")

            if len(answers) > 0:
                print(id, ' '.join(sentence.tokens))
