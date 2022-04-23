from __future__ import annotations

from coca import Sentence
from poss_ing_of import in_edges, out_edges, sentence_to_graph


def window(sentence: Sentence, center: int) -> tuple[str, str, str]:
    dependencies = sentence.dependency.to_dict()[0]
    graph = sentence_to_graph(dependencies)
    # sen = sentence.tokens

    relevant_indices = set([source for source, _, _ in in_edges(graph, center)] + [center] +
                            [target for _, target, _ in out_edges(graph, center)])

    tags = ' '.join([f"{x['text']}/{x['lemma']}/{x['xpos']}/{x['upos']}" for x in dependencies])
    all_dep = []
    rel_dep = []
    for x in dependencies:
        head = x['head']
        if head == 0:
            continue
        parent = dependencies[head - 1]
        dep = f"{x['deprel']} ({x['text']}-{x['id']}, {parent['text']}-{parent['id']})"
        all_dep.append(dep)
        if x['id'] in relevant_indices:
            rel_dep.append(dep)
    all_dep = ', '.join(all_dep)
    rel_dep = ', '.join(rel_dep)

    return tags, all_dep, rel_dep

'''
def longest_dep(sentence: Sentence, center: int) -> str:
    dependencies = sentence.dependency.to_dict()[0]
    graph = sentence_to_graph(dependencies)
    sen = sentence.tokens

    p_node = [sen[source - 1] for source, _, _ in in_edges(graph, center)]

    def longest_branch(parent: int) -> list[str]:
        max_len = 0
        branch = []
        for _, node, _ in out_edges(graph, parent):
            b = longest_branch(node)
            if len(b) > max_len:
                branch = b
                max_len = len(b)
        return [sen[parent - 1]] + branch

    return " -> ".join(p_node + longest_branch(center))
'''
