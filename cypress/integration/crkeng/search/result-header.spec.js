context("Searching", () => {
  // See: https://github.com/UAlbertaALTLab/morphodict/issues/445#:~:text=4.%20Inflected%20form
  context("result header", function () {
    const lemma = "nîmiw";
    const wordclassEmoji = "➡️"; // the arrow is the most consistent thing, which means verb
    const inflectionalCategory = /VAI-v|VAI-1/;
    const plainEnglishInflectionalCategory = "like: nipâw";
    const nonLemmaFormWithDefinition = "nîminâniwan";
    const nonLemmaFormWithoutDefinition = "ninîmin";
    const nonLemmaDefinition = "there is a dance, it is a time of dancing";

    it("should display the match wordform and word class on the same line for lemmas", function () {
      cy.visitSearch(fudgeUpOrthography(lemma));
      cy.wait(1000);

      // make sure we get at least one search result...
      cy.get('.app__content > :nth-child(1) > :nth-child(1) > :nth-child(1)').as("search-result");

      // now let's make sure the NORMATIZED form is in the search result
      cy.get(
        ':nth-child(1) > :nth-child(1) > .definition-title > .btn > a').contains(
        lemma
      );
      cy.get(":nth-child(1) > .container > .d-flex > .mb-auto > .btn").contains(
        wordclassEmoji
      );
      cy.get(":nth-child(1) > .container > .d-flex > .mb-auto > .btn").contains(
        plainEnglishInflectionalCategory
      );
    });

    it("should display the matched word form and its lemma/word class on separate lines for non-lemmas", function () {
      cy.visitSearch(fudgeUpOrthography(nonLemmaFormWithoutDefinition));
      cy.wait(1000);

      // make sure we get at least one search result...
      cy.get(".app__content > :nth-child(1) > :nth-child(1) > :nth-child(1)").as("search-result");

      // now let's make sure the NORMATIZED form is in the search result
      cy.get(
        ':nth-child(1) > :nth-child(1) > .definition-title > .btn > a').contains(
        nonLemmaFormWithoutDefinition
      );

      // now make sure the 'form of' text is below that

      cy.get('.mb-auto > .btn')
        // TODO: should we be testing for this exact text?
        .should("contain", "form of")
        .and("contain", lemma);
      cy.get('.mb-auto > .btn').should("contain", wordclassEmoji);
      cy.get('.mb-auto > .btn').should("contain",
        plainEnglishInflectionalCategory
      );
    });

    // See: https://github.com/UAlbertaALTLab/morphodict/issues/445#:~:text=4.%20Inflected%20form
    it("should display an inflected form with a definition AND its lemma", function () {
      cy.visitSearch(fudgeUpOrthography(nonLemmaFormWithDefinition));
      cy.wait(1000);

      // make sure we get at least one search result...
      cy.get('.app__content > :nth-child(1) > :nth-child(1) > :nth-child(1)').as("search-result");

      // make sure the NORMATIZED form is in the search result
      cy.get("@search-result").should(
        "contain",
        nonLemmaFormWithDefinition
      );

      // Open the linguistic breakdown popup
      cy.get(':nth-child(1) > :nth-child(1) > .definition__icon > .btn > .bi')
        .as("information-mark")
        .first()
        .click();

      // See the linguistic breakdown as an ordered list
      cy.get("@search-result")
        .should("contain", "ni-/ki- word");

      // make sure it has a definition
      cy.get("@search-result")
        // TODO: change name of [data-cy="lemma-meaning"] as it's misleading :/
        .should('contain', nonLemmaDefinition);

      // "form of nîmiw"
      cy.get("@search-result")
        .should("contain", "form of")
        .and("contain", lemma);

      cy.get("@search-result")
        .should("contain", wordclassEmoji);

      cy.get("@search-result")
        .should("contain", plainEnglishInflectionalCategory);

    });

    // See: https://github.com/UAlbertaALTLab/morphodict/issues/445#:~:text=5.%20Inflected%20form%20without%20definition
    it("should display an inflected form (without definition) and its lemma", function () {
      cy.visitSearch(fudgeUpOrthography(nonLemmaFormWithoutDefinition));
      cy.wait(1000);

      // make sure we get at least one search result...
      cy.get('#results').as("search-result");

      // make sure the NORMATIZED form is in the search result
      cy.get("@search-result").contains(
        nonLemmaFormWithoutDefinition
      );

      // Open the linguistic breakdown popup
      cy.get('.definition__icon > .btn > .bi')
        .first()
        .as("information-mark")
        .click();

      // See the linguistic breakdown as an ordered list
      cy.get("@search-result")
        .first()
        .should("be.visible")
        .contains("li", "ni-/ki- word");

      // Close the tooltip
      cy.get("@search-result").click();

      // "form of nîmiw"
      cy.get("@search-result")
        .should("contain", "form of")
        .and("contain", lemma);

      cy.get("@search-result")
        .should("contain", wordclassEmoji);

      cy.get("@search-result")
        .should("contain", plainEnglishInflectionalCategory);

      // Inflectional category tooltip
      cy.get("@search-result").should('contain', inflectionalCategory);
    });

    // See: https://github.com/UAlbertaALTLab/morphodict/issues/445#:~:text=6.%20Lemma%20definition
    it("should display the definition of a lemma", function () {
      cy.visitSearch(fudgeUpOrthography(lemma));
      cy.wait(1000);

      // make sure we get at least one search result...
      cy.get('.app__content > :nth-child(1) > :nth-child(1) > :nth-child(1)').as("search-result");

      // make sure the NORMATIZED form is in the search result
      cy.get("@search-result").should(
        'contain',
        lemma
      );

      // Open the linguistic breakdown popup
      cy.get(':nth-child(1) > :nth-child(1) > .definition__icon > .btn')
        .first()
        .as("information-mark")
        .click();

      // See the linguistic breakdown as an ordered list
      cy.get("@search-result")
        .first()
        .should("be.visible")
        .contains("li", "ni-/ki- word");

      cy.get("@search-result").click()

      cy.get(':nth-child(1) > .container > .d-flex > .mb-auto').as("elaboration");

      cy.get("@elaboration")
        .should("contain", wordclassEmoji);

      cy.get("@elaboration")
        .and("contain", plainEnglishInflectionalCategory);

      // Inflectional category tool tip
      cy.get("@elaboration").should('contain', inflectionalCategory);
    });

    // Regression: it used to display 'like — pê-' :/
    it.only("should not display wordclass emoji if it does not exist", function () {
      // Preverbs do not have an elaboration (right now)
      const preverb = "nitawi-";
      cy.visitSearch(preverb);
      cy.wait(1000);

      cy.get('.app__content > :nth-child(1) > :nth-child(1) > :nth-child(1)')
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
