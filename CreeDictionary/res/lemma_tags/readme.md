Files here store templates of common lemma analyses for each [general word class](../../../docs/glossary.md#general-word-class)

i.e. 
- NA lemmas usually have tags +N+A+Sg
- VAI lemmas usually have tags +V+AI+Ind+Prs+3Sg
- ...

i.e. It helps solve this question in the Database importer: "Which one of maskwa+N+A+Sg and maskwa+N+A+Obv is the lemma analysis?"

Files here are only used as a fallback when ambiguity exists, which happens not so often.

---

Folders here are languages this app supports.

There should be a `lemma-tags.tsv` Under each folder with two columns.

The first column is the [general word class](../../../docs/glossary.md#general-word-class)

The second column is analysis of common lemmas for the said word class. If there are multiple possibilities, 
use space to separate multiple analyses, and they should be ordered in terms of frequency.

The following is an example of three rows
```.tsv
NI  ${lemma}+N+I+Sg
NA  ${lemma}+N+A+Sg
Ipc ${lemma}+Ipc ${lemma}+Ipc+Foc
```

Note:
- ${} format to indicate where the lemma is 
- The third row has two analyses, it's interpreted as "Ipc lemmas usually takes the form of ${lemma}+Ipc, 
less often they can be ${lemma}+Ipc+Foc" too.