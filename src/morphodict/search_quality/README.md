This app contains tools for evaluating the quality of search results.

`sample.csv` contains a set of sample queries that we can use to measure
how well the search engine performs, and how that is improving over time.
It is expected to be updated and improved over time. When expected results
in `sample.csv` are changed, the analysis code will automatically use the
latest expected results for evaluation. When new queries are added, the
samples must be re-run on old checkouts of the dictionary codebase.

The query sample is currently non-representative; it just has some things
that some people have noticed that the current dictionary is either good or
bad at searching for.

The headings are:
  - **Query**: What to search for. This can be an English or cree word or
    phrase.
  - **Nêhiyawêwin 1**, **Nêhiyawêwin 2**, **Nêhiyawêwin 3**:  The best
    three possible results for the query, which we would hope to see as the
    #1, #2, and #3 results.
  - The other fields are currently unused

Results of running queries through the search engine are stored in the
`sample_results` folder in order to allow making comparisons over time. To
prevent excessive repository disk use, please do not check these files in
directly; using [Git LFS](https://git-lfs.github.com/) is ok though.

