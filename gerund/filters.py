from __future__ import annotations

from typing import Dict, Generator, Tuple

from stanza import Document

from .structs import Sentence

ID = int  # an ID is one-based
Graph = Dict[Tuple[ID, ID], str]


def document_to_graph(document: Document) -> Graph:
    """Convert `document` (i.e., dependency parse) into a directed graph

    Parameters
    ----------
    document : Document
        The dependency parse of a sentence, produced by a `stanza` parser.

    Returns
    -------
    Graph
        A `dict` of `(int, int)` to `str`. Essentially a collection of directed
        edges and their labels (i.e., dependency relationships).
    """
    assert len(document.to_dict()) == 1, "Document contains multiple sentences"

    return {(i["head"], i["id"]): i["deprel"] for i in document.to_dict()[0]}


def gerund_filter(sentence: Sentence) -> Generator[Tuple[str, ID]]:
    """Extract all gerund from the given `sentence`.

    Parameters
    ----------
    sentence : Sentence
        A COCA sentence with its `dependency` being not `None`.

    Yields
    ------
    Generator[Tuple[str, int]]
        A generator of two-element tuples, where the first element specifies the
        kind of gerund (i.e., `VBG`, `NN`, or `NNS`) and the second element
        specifies the ID of the gerund.
    """
    assert sentence.dependency is not None, "Sentence's dependency is None"

    parse = document_to_graph(sentence.dependency)
    poses = {i["head"]: i["xpos"] for i in sentence.dependency.to_dict()}

    for id, text in enumerate(sentence.tokens):
        if (poses[id] == "VBG" and
                # no amod dependency going in or out of token
                "amod" not in [v for k, v in parse.items() if id in k] and
                # no aux dependency going out of token
                "aux" not in [v for k, v in parse.items() if id == k[0]]):
            yield "VBG", id

        if poses[id] == "NN" and text.endswith("ing"):
            yield "NN", id

        if poses[id] == "NNS" and text.endswith("ings"):
            yield "NNS", id
