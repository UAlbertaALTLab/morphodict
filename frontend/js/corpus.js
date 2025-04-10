const COUNT_API = "https://korp-backend.altlab.dev/count";
const CORPUS_URL = "https://korp.altlab.dev/"
const CORPORA = getCorporaFromLocation();
function getCorporaFromLocation() {
    const location = window.location.toString();
    if (location.includes(`itwewina`) || location.includes(`crk`)) {
        return "MASKWACIS-SENTENCES,WOLFART_AHENAKEW"
    }
    if (location.includes(`ikidowinan`) || location.includes(`ciw`)) {
        return "OJIBWE"
    }
    return ""
}

function createCorpusSearchURL(wordform){
    return `${CORPUS_URL}#?corpus=${CORPORA.toLowerCase()}&search=word|${wordform}&cqp=[]`
}

export async function fetchCorpusURL(wordform) {
    if (!CORPORA) {
        return undefined
    }
    let result = await fetch(
        `${COUNT_API}?corpus=${CORPORA}&cqp=[word="${wordform}"]`)
            .then((count_request) => {
            return count_request.json()
            }).then((count_json) => {
                if (count_json["count"]){
                    return createCorpusSearchURL(wordform)
                }
            })
    return result
}