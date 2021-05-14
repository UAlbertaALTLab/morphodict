from CreeDictionary.API.search.query import Query


def test_basic_query():
    q = Query("foo")
    assert q.query_string == "foo"
    assert q.query_terms == ["foo"]
    assert q.verbose == None


def test_normalization():
    # combining circumflex
    q = Query("WA\u0302PAME\u0302W")
    assert q.query_string == "wâpamêw"
    assert q.query_terms == ["wâpamêw"]


def test_multi_word_query():
    q = Query("foo bar")
    assert q.query_string == "foo bar"
    assert q.query_terms == ["foo", "bar"]


def test_query_verbose_on():
    q = Query("verbose:true fish")
    assert q.verbose == True
    assert q.query_string == "fish"


def test_query_verbose_off():
    q = Query("verbose:0 fish")
    assert q.verbose == False
    assert q.query_string == "fish"


def test_query_auto():
    q = Query("auto:0 fish")
    assert q.auto == False
    assert q.query_string == "fish"


def test_query_valididty():
    q = Query("verbose:true")
    assert q.is_valid == False
