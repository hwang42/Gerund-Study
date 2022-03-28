from __future__ import annotations

import pickle
from typing import List, Tuple

from IPython.display import display_html

Sentence = Tuple[List[str], List[dict]]


def ensure_loaded(sentence: str | Sentence) -> Sentence:
    if isinstance(sentence, tuple):
        return sentence

    if not sentence.endswith(".pkl"):
        sentence += ".pkl"

    with open(sentence, "rb") as file:
        return pickle.load(file)


def print_sent(sentence: str | Sentence, xpos: bool = False) -> None:
    sentence = ensure_loaded(sentence)

    tokens = []
    for token in sentence[1]:
        if not xpos:
            tokens.append(('<div style="display:inline-block;margin:1px 3px;">'
                           f'{token["text"]}'
                           '</div>'))
        else:
            tokens.append(('<div style="display:inline-block;margin:1px 3px;">'
                           f'<div>{token["text"]}</div>'
                           f'<div>{token["xpos"]}</div>'
                           "</div>"))

    display_html(f"<div>{' '.join(tokens)}</div>", raw=True)


def print_parse(sentence: str | Sentence, aligned: bool = True) -> None:
    sentence = ensure_loaded(sentence)

    root = None
    edges = []
    for token in sentence[1]:
        id, head, relation = token["id"], token["head"], token["deprel"]

        if head == 0:
            root = sentence[1][id - 1]
            continue

        source, target = sentence[1][head - 1], sentence[1][id - 1]

        edges.append((source["text"], source["xpos"],
                     relation,
                     target["text"], target["xpos"]))

    print(f"Root: {root['text']} [{root['xpos']}]")

    if not aligned:
        for edge in edges:
            s_text, s_xpos, relation, t_text, t_xpos = edge

            print(f"{s_text} [{s_xpos}] -({relation})-> [{t_xpos}] {t_text}")
    else:
        s_text_width = max(len(i[0]) for i in edges)
        s_xpos_width = max(len(i[1]) for i in edges)
        relation_width = max(len(i[2]) for i in edges)
        t_text_width = max(len(i[3]) for i in edges)
        t_xpos_width = max(len(i[4]) for i in edges)

        template = ("{:>"f"{s_text_width}""} [{:^"f"{s_xpos_width}""}]"
                    " -({:^"f"{relation_width}""})-> "
                    "[{:^"f"{t_xpos_width}""}] {:<"f"{t_text_width}""}")

        for edge in edges:
            print(template.format(edge[0], edge[1], edge[2], edge[4], edge[3]))
