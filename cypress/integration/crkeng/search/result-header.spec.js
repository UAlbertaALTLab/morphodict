context("Searching", () => {
  // See: https://github.com/UAlbertaALTLab/morphodict/issues/445#:~:text=4.%20Inflected%20form
  context("result header", function () {
    const lemma = "nîmiw";
    const wordclassEmoji = "➡️"; // the arrow is the most consistent thing, which means verb
    const inflectionalCategory = /VAI-v|VAI-1/;
    const plainEnglishInflectionalCategory = "like: nipâw";
    const nonLemmaFormWithDefinition = "nîminâniwan";
    const nonLemmaFormWithoutDefinition = "ninîmin";
    const nonLemmaDefinition = "it is a dance";

    it("should display the match wordform and word class on the same line for lemmas", function () {
      cy.visitSearch(fudgeUpOrthography(lemma));

      // make sure we get at least one search result...
      cy.get("[data-cy=search-result]").as("search-result");

      // now let's make sure the NORMATIZED form is in the search result
      cy.get("@search-result").contains(
        'header [data-cy="matched-wordform"]',
        lemma
      );
      cy.get("@search-result").contains(
        'header [data-cy="word-class"]',
        wordclassEmoji
      );
      cy.get("@search-result").contains(
        'header [data-cy="word-class"]',
        plainEnglishInflectionalCategory
      );
    });

    it("should display the matched word form and its lemma/word class on separate lines for non-lemmas", function () {
      cy.visitSearch(fudgeUpOrthography(nonLemmaFormWithoutDefinition));

      // make sure we get at least one search result...
      cy.get("[data-cy=search-result]").as("search-result");

      // now let's make sure the NORMATIZED form is in the search result
      cy.get("@search-result").contains(
        'header [data-cy="matched-wordform"]',
        nonLemmaFormWithoutDefinition
      );

      // now make sure the 'form of' text is below that
      cy.get("@search-result")
        .get('header [data-cy="elaboration"]')
        .as("elaboration");

      cy.get("@elaboration")
        .get('[data-cy="reference-to-lemma"]')
        // TODO: should we be testing for this exact text?
        .should("contain", "form of")
        .and("contain", lemma);
      cy.get("@elaboration").contains('[data-cy="word-class"]', wordclassEmoji);
      cy.get("@elaboration").contains(
        '[data-cy="word-class"]',
        plainEnglishInflectionalCategory
      );
    });

    // See: https://github.com/UAlbertaALTLab/morphodict/issues/445#:~:text=4.%20Inflected%20form
    it("should display an inflected form with a definition AND its lemma", function () {
      cy.visitSearch(fudgeUpOrthography(nonLemmaFormWithDefinition));

      // make sure we get at least one search result...
      cy.get("[data-cy=search-result]").as("search-result");

      // make sure the NORMATIZED form is in the search result
      cy.get("@search-result").contains(
        'header [data-cy="matched-wordform"]',
        nonLemmaFormWithDefinition
      );

      // Open the linguistic breakdown popup
      cy.get("@search-result")
        .find("[data-cy=information-mark]")
        .as("information-mark")
        .first()
        .click();

      // See the linguistic breakdown as an ordered list
      cy.get("[data-cy=linguistic-breakdown]")
        .first()
        .should("be.visible")
        .contains("li", "ni-/ki- word");

      // Close the tooltip
      cy.get("@information-mark").first().blur();

      // make sure it has a definition
      cy.get("@search-result")
        // TODO: change name of [data-cy="lemma-meaning"] as it's misleading :/
        .contains('[data-cy="lemma-meaning"]', nonLemmaDefinition);

      // "form of nîmiw"
      cy.get("@search-result")
        .get('[data-cy="reference-to-lemma"]')
        .should("contain", "form of")
        .and("contain", lemma);

      cy.get("@search-result").get('[data-cy="elaboration"]').as("elaboration");

      cy.get("@elaboration")
        .get('[data-cy="word-class"]')
        .should("contain", wordclassEmoji)
        .and("contain", plainEnglishInflectionalCategory);

      // Inflectional category tool tip
      cy.get("@elaboration").get('[data-cy="word-class"]').first().click();
      cy.get("@elaboration").get('[role="tooltip"]').should("be.visible");
      cy.get("@elaboration").contains('[role="tooltip"]', inflectionalCategory);
    });

    // See: https://github.com/UAlbertaALTLab/morphodict/issues/445#:~:text=5.%20Inflected%20form%20without%20definition
    it("should display an inflected form (without definition) and its lemma", function () {
      cy.visitSearch(fudgeUpOrthography(nonLemmaFormWithoutDefinition));

      // make sure we get at least one search result...
      cy.get("[data-cy=search-result]").as("search-result");

      // make sure the NORMATIZED form is in the search result
      cy.get("@search-result").contains(
        'header [data-cy="matched-wordform"]',
        nonLemmaFormWithoutDefinition
      );

      // Open the linguistic breakdown popup
      cy.get("@search-result")
        .get("[data-cy=information-mark]")
        .first()
        .as("information-mark")
        .click();

      // See the linguistic breakdown as an ordered list
      cy.get("[data-cy=linguistic-breakdown]")
        .first()
        .should("be.visible")
        .contains("li", "ni-/ki- word");

      // Close the tooltip
      cy.get("@information-mark").blur();

      // "form of nîmiw"
      cy.get("@search-result")
        .get('[data-cy="reference-to-lemma"]')
        .should("contain", "form of")
        .and("contain", lemma);

      cy.get("@search-result").get('[data-cy="elaboration"]').as("elaboration");

      cy.get("@elaboration")
        .get('[data-cy="word-class"]')
        .should("contain", wordclassEmoji)
        .and("contain", plainEnglishInflectionalCategory);

      // Inflectional category tooltip
      cy.get("@elaboration").get('[data-cy="word-class"]').first().click();
      cy.get("@elaboration").get('[role="tooltip"]').should("be.visible");
      cy.get("@elaboration").contains('[role="tooltip"]', inflectionalCategory);
    });

    // See: https://github.com/UAlbertaALTLab/morphodict/issues/445#:~:text=6.%20Lemma%20definition
    it("should display the definition of a lemma", function () {
      cy.visitSearch(fudgeUpOrthography(lemma));

      // make sure we get at least one search result...
      cy.get("[data-cy=search-result]").as("search-result");

      // make sure the NORMATIZED form is in the search result
      cy.get("@search-result").contains(
        'header [data-cy="matched-wordform"]',
        lemma
      );

      // Open the linguistic breakdown popup
      cy.get("@search-result")
        .get("[data-cy=information-mark]")
        .first()
        .as("information-mark")
        .click();

      // See the linguistic breakdown as an ordered list
      cy.get("[data-cy=linguistic-breakdown]")
        .first()
        .should("be.visible")
        .contains("li", "ni-/ki- word");

      // Close the tooltip
      cy.get("@information-mark").blur();

      cy.get("@search-result").get('[data-cy="elaboration"]').as("elaboration");

      cy.get("@elaboration")
        .get('[data-cy="word-class"]')
        .should("contain", wordclassEmoji)
        .and("contain", plainEnglishInflectionalCategory);

      // Inflectional category tool tip
      cy.get("@elaboration").get('[data-cy="word-class"]').first().click();
      cy.get("@elaboration").get('[role="tooltip"]').should("be.visible");
      cy.get("@elaboration").contains('[role="tooltip"]', inflectionalCategory);
    });

    // Regression: it used to display 'like — pê-' :/
    it("should not display wordclass emoji if it does not exist", function () {
      // Preverbs do not have an elaboration (right now)
      const preverb = "nitawi-";
      cy.visitSearch(preverb);

      cy.get("[data-cy=search-result]")
        .first()
        .find("[data-cy=word-class]")
        .should("contain", "like: pê-")
        .and("not.contain", "None");
    });

    /**
     * @returns {String} the wordform, as if you typed very quickly on your niece's peanut butter-smeared iPad
     */
    function fudgeUpOrthography(normatizedWordform) {
      return normatizedWordform
        .normalize("NFKD")
        .replace(/[\u0300-\u035f-]/g, "")
        .toLowerCase();
    }
  });
});
