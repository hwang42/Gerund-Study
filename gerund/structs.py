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
