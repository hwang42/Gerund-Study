Parsing data from corpus -- the data in the corpus is formatted to avoid copyright infringement, so there are @ symbols inserted in some of the text to avoid full reproduction of the sentence. The first step of the process of producing the gerunds is removing these sentences and parsing the output from running the corpus through stanza. This collects the information from the dependency parse that stanza produces.  

--- Run Instructions --- 
in command line (with environment activated), run command "python main.py [filename of the text to parse] [directory for pkl file outputs]" 
if no directory is provided, the pkl files will be generated in the current directory

--- Files Used --- 
main.py
within the gerund module
  structs.py


--- Input ---
txt file with the corpus of sentences to parse
directory for output pkl files

--- Output ---
generated pkl files containing the stanza dependency parse of each sentence in the current folder
    [id (text-paragraph-sentence), sentence tokens, for each token list of dependency information in the format {word id, text, lemma, upos, xpos, features, head of sentence id, deprel, misc, starting character, ending character}]
    
    
    example of the dependency information for each token:
    {'id': 1, 'text': 'It', 'lemma': 'it', 'upos': 'PRON', 'xpos': 'PRP', 'feats': 'Case=Nom|Gender=Neut|Number=Sing|Person=3|PronType=Prs', 'head': 5, 'deprel': 'nsubj', 'misc': '', 'start_char': 0, 'end_char': 2}
    this information is taken from the stanza parse of the sentence
   
--- Note ---
To access the information about individual tokens, use the function dependency.to_dict() on the relevant dependency list