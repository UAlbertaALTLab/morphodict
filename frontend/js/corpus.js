const COUNT_API = "https://korp-backend.altlab.dev/count";
const CORPUS_URL = "https://korp.altlab.dev/";
const CORPORA = getCorporaFromLocation();
function getCorporaFromLocation() {
  const location = window.location.toString();
  if (location.includes(`itwewina`) || location.includes(`crk`)) {
    return "MASKWACIS-SENTENCES,WOLFART_AHENAKEW";
  }
  if (location.includes(`ikidowinan`) || location.includes(`ciw`)) {
    return "OJIBWE";
  }
  return "";
}

function createCorpusSearchURL(wordform, lemma) {
  if (lemma) {
    return `${CORPUS_URL}#?corpus=${CORPORA.toLowerCase()}&search=cqp|[lemma=\"${wordform}\"]&cqp=[]`;
  }
  return `${CORPUS_URL}#?corpus=${CORPORA.toLowerCase()}&search=word|${wordform}&cqp=[]`;
}

export async function fetchCorpusURL(wordform, lemma = false) {
  if (!CORPORA) {
    return undefined;
  }
  let key = lemma ? "lemma" : "word";
  let result = await fetch(
    `${COUNT_API}?corpus=${CORPORA}&cqp=[${key}="${wordform}"]`
  )
    .then((count_request) => {
      return count_request.json();
    })
    .then((count_json) => {
      if (count_json["count"]) {
        return createCorpusSearchURL(wordform, lemma);
      }
    });
  return result;
}
