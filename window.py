from poss_ing_of import sentence_to_graph, in_edges, out_edges
from coca import Sentence


def window(sentence: Sentence, center: int) -> list[int]:
    dependencies = sentence.dependency.to_dict()[0]
    graph = sentence_to_graph(dependencies)
    return [source for source, _, _ in in_edges(graph, center)] + [target for _, target, _ in out_edges(graph, center)]
