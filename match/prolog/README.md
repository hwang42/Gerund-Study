# README for `main-v2.py`

As discussed during class, the celexjfile contain multi-word patterns which cannot be effectively handled by the Prolog-based sentence matcher. Therefore, for the sake of preserving the most amount of information, the following approach will be followed:

For every sentence, the three difference patterns, as specified by the Google Docs, will be search for and all possible matches will be reported. However, for cases that matches the second or the third pattern, no matter what the ing-word actually is, the sentence will be output, along with the recommendation for exclusion or inclusion, according to the celex file.

The recommendation is computed as following:

1. All matches with the celex file are not case-sensitive.
2. The match will be made against the last word of each entry (typically the ing-word).
3. Once all matches has been found and grouped:
   1. If all celex classifications for those matches are the same, recommend that.
   2. Otherwise, recommend the classification with the highest occurrence with "?" attached.
