from __future__ import annotations

from nltk.tokenize import PunktSentenceTokenizer

from .types import Paragraph, Sentence, Text

tokenizer = PunktSentenceTokenizer()

def sentences_from_tokens(tokens: list[str]) -> list[Sentence]:
    print(' '.join(tokens))
    return [Sentence(s) for s in tokenizer.sentences_from_tokens(tokens)]


def paragraphs_from_tokens(tokens: list[str]) -> list[Paragraph]:
    indexes = [i for i, t in enumerate(tokens) if t == "<p>"]
    spans = zip([0] + [i + 1 for i in indexes], indexes)

    return [Paragraph(sentences_from_tokens(tokens[i:j])) for i, j in spans]


def text_from_tokens(tokens: list[str]) -> Text:
    text_id, *content = tokens

    print("{:-^80}".format(f" {text_id}"))

    return Text(text_id, paragraphs_from_tokens(content))


def load_coca(filename: str) -> list[Text]:
    with open(filename, "r") as file:
        return [text_from_tokens(l.split()) for l in file if l.startswith("##")]
