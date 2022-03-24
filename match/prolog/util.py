from __future__ import annotations

from typing import Generator

from coca import Sentence, Text
from pyswip import Prolog

reasoner = Prolog()


def sentence_iterator(text: Text, keep_skipped: bool = False) -> Generator[tuple[str, Sentence]]:
    for p_idx, paragraph in enumerate(text.paragraphs):
        for s_idx, sentence in enumerate(paragraph.sentences):
            if keep_skipped or not sentence.skipped:
                yield f"{text.text_id[2:]}-{p_idx}-{s_idx}", sentence


def sentence_to_prolog(sentence: Sentence) -> list[str]:
    dependencies = sentence.dependency.to_dict()[0]

    text_clauses, xpos_clauses, edge_clauses = [], [], []
    for token in dependencies:
        # generate text clause
        id, text = token["id"], token["text"].replace('"', '\\"')
        text_clauses.append(f'text({id}, "{text}").')

        # generate xpos clause
        xpos = token["xpos"]
        xpos_clauses.append(f"xpos({id}, '{xpos}').")

        # generate edge clause
        head, edge = token["head"], token["deprel"]
        edge_clauses.append(f"edge({head}, {id}, '{edge}').")

    return text_clauses + xpos_clauses + edge_clauses


def sentence_search(sentence: Sentence, pattern: list[str], query: str) -> bool:
    # insert sentence clauses
    for clause in sentence_to_prolog(sentence):
        reasoner.assertz(clause[:-1])

    # insert pattern clauses
    for clause in pattern:
        reasoner.assertz(clause[:-1])

    # pattern matching and determine result
    matched = True
    try:
        next(reasoner.query(query))
    except StopIteration:
        matched = False  # no answer at all

    # reset reasoner
    reasoner.retractall("text(_, _)")
    reasoner.retractall("xpos(_, _)")
    reasoner.retractall("edge(_, _, _)")

    for clause in pattern:
        reasoner.retract(clause[:-1])

    return matched
