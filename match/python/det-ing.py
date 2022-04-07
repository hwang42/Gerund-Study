

def det_ing(sentence_deps, word):
    for dependency in sentence_deps:
        if dependency.deprel == 'det' and dependency.head == word:
            return True
    return False

