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
      cy.wait(3000);

      // make sure we get at least one search result...
      cy.get('[data-cy=all-search-results]').first().as("search-result");

      // now let's make sure the NORMATIZED form is in the search result
      cy.get(
        '[data-cy=lemmaLink]').contains(
        lemma
      );
      cy.get("[data-cy=elaboration]").first().contains(
        wordclassEmoji
      );
      cy.get("[data-cy=elaboration]").first().contains(
        plainEnglishInflectionalCategory
      );
    });

    it("should display the matched word form and its lemma/word class on separate lines for non-lemmas", function () {
      cy.visitSearch(fudgeUpOrthography(nonLemmaFormWithoutDefinition));
      cy.wait(3000);

      // make sure we get at least one search result...
      cy.get("[data-cy=all-search-results]").first().as("search-result");

      // now let's make sure the NORMATIZED form is in the search result
      cy.get(
        '[data-cy=lemmaLink]').contains(
        nonLemmaFormWithoutDefinition
      );

      // now make sure the 'form of' text is below that

      cy.get('@search-result')
        // TODO: should we be testing for this exact text?
        .should("contain", "Form of")
        .and("contain", lemma);
      cy.get('[data-cy=elaboration]').first().should("contain", wordclassEmoji);
      cy.get('[data-cy=elaboration]').first().should("contain",
        plainEnglishInflectionalCategory
      );
    });

    // See: https://github.com/UAlbertaALTLab/morphodict/issues/445#:~:text=4.%20Inflected%20form
    it("should display an inflected form with a definition AND its lemma", function () {
      cy.visitSearch(fudgeUpOrthography(nonLemmaFormWithDefinition));
      cy.wait(1000);

      // make sure we get at least one search result...
      cy.get("[data-cy=all-search-results]").first().as("search-result");

      // make sure the NORMATIZED form is in the search result
      cy.get("@search-result").should(
        "contain",
        nonLemmaFormWithDefinition
      );

      // Open the linguistic breakdown popup
      cy.get('[data-cy=infoButton]')
          .first()
        .as("information-mark")
        .click();

      // See the linguistic breakdown as an ordered list
      cy.get("[data-cy=infoButtonInfo]")
        .should("contain", "ni-/ki- word");

      // make sure it has a definition
      cy.get("@search-result")
        // TODO: change name of [data-cy="lemma-meaning"] as it's misleading :/
        .should('contain', nonLemmaDefinition);

      // "form of nîmiw"
      cy.get("@search-result")
        .should("contain", "Form of")
        .and("contain", lemma);

      cy.get("@search-result")
        .should("contain", wordclassEmoji);

      cy.get("@search-result")
        .should("contain", plainEnglishInflectionalCategory);

    });

    // See: https://github.com/UAlbertaALTLab/morphodict/issues/445#:~:text=5.%20Inflected%20form%20without%20definition
    it("should display an inflected form (without definition) and its lemma", function () {
      cy.visitSearch(fudgeUpOrthography(nonLemmaFormWithoutDefinition));
      cy.wait(2000);

      // make sure we get at least one search result...
      cy.get("[data-cy=all-search-results]").first().as("search-result");

      // make sure the NORMATIZED form is in the search result
      cy.get("@search-result").contains(
        nonLemmaFormWithoutDefinition
      );

      // Open the linguistic breakdown popup
      cy.get('[data-cy=infoButton]')
        .first()
        .as("information-mark")
        .click();

      // See the linguistic breakdown as an ordered list
      cy.get("[data-cy=infoButtonInfo]")
        .first()
        .should("be.visible")
        .contains("ni-/ki- word");

      // Close the tooltip
      cy.get("@search-result").click();

      // "form of nîmiw"
      cy.get("@search-result")
        .should("contain", "Form of")
        .and("contain", lemma);

      cy.get("@search-result")
        .should("contain", wordclassEmoji);

      cy.get("@search-result")
        .should("contain", plainEnglishInflectionalCategory);

      // Inflectional category tooltip
      cy.get("@search-result").contains(inflectionalCategory);
    });

    // See: https://github.com/UAlbertaALTLab/morphodict/issues/445#:~:text=6.%20Lemma%20definition
    it("should display the definition of a lemma", function () {
      cy.visitSearch(fudgeUpOrthography(lemma));
      cy.wait(3000);

      // make sure we get at least one search result...
      cy.get("[data-cy=all-search-results]").first().as("search-result");

      // make sure the NORMATIZED form is in the search result
      cy.get("@search-result").should(
        'contain',
        lemma
      );

      // Open the linguistic breakdown popup
      cy.get('[data-cy=infoButton]')
        .first()
        .as("information-mark")
        .click();

      // See the linguistic breakdown as an ordered list
      cy.get("[data-cy=infoButtonInfo]")
        .first()
        .should("be.visible")
        .contains("ni-/ki- word");

      cy.get('[data-cy=definitionText]').first().click();

      cy.get('[data-cy=elaboration]').first().as("elaboration");

      cy.get("@elaboration")
        .should("contain", wordclassEmoji);

      cy.get("@elaboration")
        .and("contain", plainEnglishInflectionalCategory);

      // Inflectional category tool tip
      cy.get("@search-result").contains(inflectionalCategory);
    });

    // Regression: it used to display 'like — pê-' :/
    it("should not display wordclass emoji if it does not exist", function () {
      // Preverbs do not have an elaboration (right now)
      const preverb = "nitawi-";
      cy.visitSearch(preverb);
      cy.wait(2000);

      cy.get('[data-cy=all-search-results').first()
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
