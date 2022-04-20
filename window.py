from __future__ import annotations

from coca import Sentence
from poss_ing_of import in_edges, out_edges, sentence_to_graph


def window(sentence: Sentence, center: int) -> str:
    dependencies = sentence.dependency.to_dict()[0]
    graph = sentence_to_graph(dependencies)
    sen = sentence.tokens

    win = [[sen[source-1] for source, _, _ in in_edges(graph, center)],
            [sen[target-1] for _, target, _ in out_edges(graph, center)]]

    return ', '.join(win[0]) + " -> " + sen[center-1] + " -> " + ', '.join(win[1])


def longest_dep(sentence: Sentence, center: int) -> str:
    dependencies = sentence.dependency.to_dict()[0]
    graph = sentence_to_graph(dependencies)
    sen = sentence.tokens

    p_node = [sen[source-1] for source, _, _ in in_edges(graph, center)]

    def longest_branch(parent: int) -> list[str]:
        max_len = 0
        branch = []
        for _, node, _ in out_edges(graph, parent):
            b = longest_branch(node)
            if len(b) > max_len:
                branch = b
                max_len = len(b)
        return [sen[parent-1]] + branch

    return " -> ".join(p_node + longest_branch(center))
