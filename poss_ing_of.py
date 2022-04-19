from __future__ import annotations

from typing import Generator

from coca import Sentence, Text


def sentence_iterator(text: Text) -> Generator[tuple[str, Sentence]]:
    for p_idx, paragraph in enumerate(text.paragraphs):
        for s_idx, sentence in enumerate(paragraph.sentences):
            yield f"{text.text_id[2:]}-{p_idx}-{s_idx}", sentence


def sentence_to_graph(dependencies: list[dict]) -> dict[tuple[int, int], str]:
    return {(i["head"], i["id"]): i["deprel"]
            for i in dependencies}


def in_edges(graph: dict[tuple[int, int], str], node: int) -> Generator[tuple[int, int, str]]:
    for (source, target), relation in graph.items():
        if target == node:
            yield source, target, relation


def out_edges(graph: dict[tuple[int, int], str], node: int) -> Generator[tuple[int, int, str]]:
    for (source, target), relation in graph.items():
        if source == node:
            yield source, target, relation


def poss_ing_of(sentence: Sentence, centers: list[int] | None = None) -> Generator[int, str]:
    dependencies = sentence.dependency.to_dict()[0]
    graph = sentence_to_graph(dependencies)

    def has_of(center: int) -> bool:
        return any(sentence.tokens[target - 1] == "of" and relation == "case"
                   for _, target, relation
                   in out_edges(graph, center))

    # if centers is provided, only check those centers; otherwise, check all
    for center in centers:
        # poss: center -nmod:poss-> ???
        poss = any(relation == "nmod:poss"
                   for _, _, relation
                   in out_edges(graph, center))

        # of: center -nmod-> ??? -case-> of
        of = any(relation == "nmod" and has_of(target)
                 for _, target, relation
                 in out_edges(graph, center))

        # det: Detecting DET-ING tag
        det = any(relation == "det"
                    for _, _, relation
                    in out_edges(graph, center))

        # acc: Detecting ACC-ING tags
        # acc0 = any(dependencies[source-1]['upos'] in ("PRON", "PROPN") or dependencies[source-1]['xpos'] == "NN"
        #             for source, _, _
        #             in in_edges(graph, center))


        # acc1 = any(dependencies[source-1]['upos'] == "ADV"
        #            for source, _, _ in in_edges(graph, center)
        #                 for src, _, _ in in_edges(graph, source)
        #                     if dependencies[src-1]['upos'] in ("PRON", "PROPN") or dependencies[src-1]['xpos'] == "NN")

        # acc = acc0 or acc1

        #check xpos/upos of previous index in sentence: 
        # either center-1 is PRON/PROPN/NN
        acc0 = False
        if center-2 >= 0:
            acc0 = dependencies[center-2]['upos'] in ("PRON", "PROPN") or dependencies[center-2]['xpos'] == "NN"
        # or center-1 is ADV and center-2 is PRON/PROPN/NN
        acc1 = False
        if center-2 >= 0 and center-3 >= 0:
            acc1 = dependencies[center-2]['upos'] == "ADV" and (dependencies[center-3]['upos'] in ("PRON", "PROPN") or dependencies[center-2]['xpos'] == "NN")
        acc = acc0 or acc1
        # TODO: Add Relevant Dependencies Column

        if poss and of:
            yield center, "poss-ing-of"
        elif poss:
            yield center, "poss-ing"
        elif of:
            yield center, "ing-of"
        elif det:
            yield center, "det-ing"
        elif acc:
            yield center, "acc-ing"
        else:
            yield  center, "vp-ing"

def det_ing(sentence: Sentence, centers: list[int] | None = None) -> Generator[int, str]:
    dependencies = sentence.dependency.to_dict()[0]
    graph = sentence_to_graph(dependencies)

    for center in centers if centers else range(1, 1 + len(sentence.tokens)):
        #has a det out edge from center
        det =  any(relation == "det"
                    for _, _, relation
                    in out_edges(graph, center))
        if det:
            yield center, "det-ing"

# proposed hierarchy: poss-ing-of, ing-of, poss-ing, acc-ing, det-ing, vp-ing