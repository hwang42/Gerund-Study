from __future__ import annotations

from typing import Generator

from coca import Sentence, Text


def sentence_iterator(text: Text) -> Generator[tuple[str, Sentence]]:
    for p_idx, paragraph in enumerate(text.paragraphs):
        for s_idx, sentence in enumerate(paragraph.sentences):
            yield f"{text.text_id[2:]}-{p_idx}-{s_idx}", sentence


def sentence_to_graph(sentence: Sentence) -> dict[tuple[int, int], str]:
    return {(i["head"], i["id"]): i["deprel"]
            for i in sentence.dependency.to_dict()[0]}


def in_edges(graph: dict[tuple[int, int], str], node: int) -> Generator[tuple[int, int, str]]:
    for (source, target), relation in graph.items():
        if target == node:
            yield source, target, relation


def out_edges(graph: dict[tuple[int, int], str], node: int) -> Generator[tuple[int, int, str]]:
    for (source, target), relation in graph.items():
        if source == node:
            yield source, target, relation


def poss_ing_of(sentence: Sentence, centers: list[int] | None = None) -> Generator[int, str]:
    graph = sentence_to_graph(sentence)

    def has_of(center: int) -> bool:
        return any(sentence.tokens[target - 1] == "of" and relation == "case"
                   for _, target, relation
                   in out_edges(graph, center))

    # if centers is provided, only check those centers; otherwise, check all
    for center in centers if centers else range(1, 1 + len(sentence.tokens)):
        # poss: center -nmod:poss-> ???
        poss = any(relation == "nmod:poss"
                   for _, _, relation
                   in out_edges(graph, center))

        # of: center -nmod-> ??? -case-> of
        of = any(relation == "nmod" and has_of(target)
                 for _, target, relation
                 in out_edges(graph, center))

        if poss and of:
            yield center, "poss-ing-of"
        elif poss:
            yield center, "poss-ing"
        elif of:
            yield center, "ing-of"

def det_ing(sentence: Sentence, centers: list[int] | None = None) -> Generator[int, str]:
    graph = sentence_to_graph(sentence)

    for center in centers if centers else range(1, 1 + len(sentence.tokens)):
        #has a det out edge from center
        det =  any(relation == "det"
                    for _, _, relation
                    in out_edges(graph, center))
        if det:
            yield center, "det-ing"

# proposed hierarchy: poss-ing-of, ing-of, poss-ing, acc-ing, det-ing, vp-ing