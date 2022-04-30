from __future__ import annotations

from dataclasses import dataclass
from email.generator import Generator
from typing import ClassVar, List, Optional, Tuple

from nltk.tokenize import PunktSentenceTokenizer
from stanza import Document, Pipeline

PUNKT = PunktSentenceTokenizer()


@dataclass
class Sentence:
    """Dataclass for a COCA sentence and its dependency parse

    A COCA sentence contains a list of `tokens`.

    A COCA sentence is considered `skipped` if its `tokens` contain "@", such a
    sentence is not parsed due to being an incomplete sentence and has its
    `dependency` set to `None`.
    """
    parser: ClassVar[Optional[Pipeline]] = None

    tokens: List[str]
    skipped: bool = True
    dependency: Optional[Document] = None

    def __post_init__(self) -> None:
        self.skipped = "@" in self.tokens

        if not self.skipped:
            if Sentence.parser is None:
                # initialize stanza parser if not already initialized
                Sentence.parser = Pipeline(
                    lang="en",
                    tokenize_pretokenized=True,
                    processors="tokenize,mwt,pos,lemma,depparse"
                )

            self.dependency = Sentence.parser(" ".join(self.tokens))


@dataclass
class Paragraph:
    """Dataclass for a COCA paragraph

    A COCA paragraph contains a list of `sentences`.
    """
    sentences: List[Sentence]


@dataclass
class Text:
    """Dataclass for a COCA text and its ID

    A COCA text contains a list of `paragraphs`.

    The `text_id` is set to the ID of the text (e.g., `##4000161`).
    """
    text_id: str
    paragraphs: List[Paragraph]


def sentences_from_tokens(tokens: List[str]) -> List[Sentence]:
    return [Sentence(i) for i in PUNKT.sentences_from_tokens(tokens)]


def paragraphs_from_tokens(tokens: List[str]) -> List[Paragraph]:
    indexes = [i for i, j in enumerate(tokens) if j == "<p>"]
    indexes = [slice(i + 1, j) for i, j in zip([-1] + indexes, indexes)]

    return [Paragraph(sentences_from_tokens(tokens[i])) for i in indexes]


def text_from_tokens(tokens: List[str]) -> Text:
    text_id, *tokens = tokens

    return Text(text_id, paragraphs_from_tokens(tokens))


def load_coca(filename: str) -> List[Text]:
    with open(filename, "r") as file:
        return [text_from_tokens(i.split()) for i in file if i.startswith("##")]


def sentence_iterator(text: Text) -> Generator[Tuple[str, Sentence]]:
    for p_idx, paragraph in enumerate(text.paragraphs):
        for s_idx, sentence in enumerate(paragraph.sentences):
            yield f"{text.text_id[2:]}-{p_idx}-{s_idx}", sentence


def sentence_to_graph(dependencies: list[dict]) -> dict[tuple[int, int], str]:
    return {(i["head"], i["id"]): i["deprel"]
            for i in dependencies}


def in_edges(graph: dict[tuple[int, int], str], node: int) -> Generator[Tuple[int, int, str]]:
    for (source, target), relation in graph.items():
        if target == node:
            yield source, target, relation


def out_edges(graph: dict[tuple[int, int], str], node: int) -> Generator[Tuple[int, int, str]]:
    for (source, target), relation in graph.items():
        if source == node:
            yield source, target, relation


# categorize each center by type of gerund, using boolean variables to mark relevant features as true/false
def classify_gerunds(sentence: Sentence, centers: list[int] | None = None) -> Generator[int, str]:
    dependencies = sentence.dependency.to_dict()[0]
    graph = sentence_to_graph(dependencies)

    # does center have an relation going to "of"?
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

        # check xpos/upos of previous index in sentence: dependencies is 0-indexed and center is 1-indexed
        # either center-1 is PRON/PROPN/NN
        acc0 = False
        if center-2 >= 0:
            acc0 = dependencies[center-2]['upos'] in (
                "PRON", "PROPN") or dependencies[center-2]['xpos'] == "NN"
        # or center-1 is ADV and center-2 is PRON/PROPN/NN
        acc1 = False
        if center-2 >= 0 and center-3 >= 0:
            acc1 = dependencies[center-2]['upos'] == "ADV" and (dependencies[center-3]['upos'] in (
                "PRON", "PROPN") or dependencies[center-2]['xpos'] == "NN")
        acc = acc0 or acc1

        # use boolean variables to determine category, starting with most specific and ending with vp-ing as a default case
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
            yield center, "vp-ing"
