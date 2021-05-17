from CreeDictionary.DatabaseManager.cree_inflection_generator import expand_inflections


def test_expand_inflections():
    results = expand_inflections(
        ["kinêpikos+N+A+Sg", "mawinêskomêw+V+TA+Ind+3Sg+4Sg/PlO"], verbose=False
    )
    kinepikos_results = results["kinêpikos+N+A+Sg"]
    mawineskomew_results = results["mawinêskomêw+V+TA+Ind+3Sg+4Sg/PlO"]

    # it should has the original lemma form
    assert ("kinêpikos+N+A+Sg", {"kinêpikos"}) in kinepikos_results
    assert (
        "mawinêskomêw+V+TA+Ind+3Sg+4Sg/PlO",
        {"mawinêskomêw"},
    ) in mawineskomew_results

    # it should have some other inflected forms
    assert ("kinêpikos+N+A+Obv", {"kinêpikosa"}) in kinepikos_results
    assert (
        "PV/e+mawinêskomêw+V+TA+Cnj+2Sg+1SgO",
        {"ê-mawinêskomiyan"},
    ) in mawineskomew_results

    # the function should also work on IPCs
    ipc_result = expand_inflections(["tastawayakap+Ipc"], verbose=False)
    assert ipc_result == {"tastawayakap+Ipc": [("tastawayakap+Ipc", {"tastawayakap"})]}
