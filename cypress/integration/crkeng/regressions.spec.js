context("Regressions", () => {
  /**
   * Cypress does not URL-encode non-ASCII components in URLs automatically,
   * but many of our test cases become dramatically easier to write if this
   * magic is done for us. So, test that this is the case!
   */
  it("should handle a non-ASCII letter in the URL properly", () => {
    cy.visitSearch("acâhkos");
    cy.wait(6000);

    cy.get("[data-cy='definitionTitle']").first().should("contain", "acâhkos");
  });

  // https://github.com/UAlbertaALTLab/morphodict/issues/147
  it("should allow space characters in exact strings", () => {
    cy.visitSearch("acâhkos kâ-osôsit");
    cy.wait(3000);
    cy.get("[data-cy='definitionTitle']").first().should("contain", "acâhkos kâ-osôsit");

    cy.visitSearch("acâhkosa kâ-otakohpit");
    cy.wait(3000);
    cy.get("[data-cy='definitionTitle']").first().should(
      "contain",
      "acâhkosa kâ-otakohpit"
    );
  });

  // https://github.com/UAlbertaALTLab/morphodict/issues/147
  it("should allow space characters in spell-relaxed results", () => {
    cy.visitSearch("niki nitawi kiskinwahamakosin");
    cy.wait(5000);
    cy.get("[data-cy='definitionTitle']").first().should("contain", "nikî-nitawi-kiskinwahamâkosin");

    cy.visitSearch("ka ki awasisiwiyan");
    cy.wait(5000);
    cy.get("[data-cy='definitionTitle']").first().should("contain", "ka-kî-awâsisîwiyan");

    cy.visitSearch("e nipat");
    cy.wait(35000);
    cy.get("[data-cy='definitionTitle']").first().should("contain", "ê-nipât");
  });

  // https://github.com/UAlbertaALTLab/morphodict/issues/158
  it("should display relevant English results", () => {
    cy.visitSearch("see");
    cy.wait(10000);
    cy.get('[data-cy=all-search-results]')
      .should("contain", "wâpiw")
      .and("contain", "wâpahtam")
      .and("contain", "wâpamêw");

    cy.visitSearch("eat");
    cy.wait(10000);
    cy.get('[data-cy=all-search-results]')
      .should("contain", "mîcisow")
      .and("contain", "mîciw")
      .and("contain", "mowêw");

    cy.visitSearch("sleep");
    cy.wait(8000);
    cy.get('[data-cy=all-search-results]').should("contain", "nipâw");
  });

  // https://github.com/UAlbertaALTLab/morphodict/issues/161
  it("should show preverbs", () => {
    cy.visitSearch("ati");
    cy.wait(4000);
    cy.get("[data-cy='definitionTitle']").should("contain", "ati-");

    cy.visitSearch("ati-");
    cy.wait(4000);
    cy.get("[data-cy='definitionTitle']").should("contain", "ati-");

    cy.visitSearch("nitawi");
    cy.wait(4000);
    cy.get("[data-cy='definitionTitle']").should("contain", "nitawi-");

    cy.visitSearch("pe");
    cy.wait(4000);
    cy.get("[data-cy='definitionTitle']").should("contain", "pê-");
  });

  // https://github.com/UAlbertaALTLab/morphodict/issues/160
  it("should show results for pronouns", () => {
    cy.visitSearch("oma");
    cy.wait(8000);
    cy.get("[data-cy='definitionTitle']").should("contain", "ôma");

    cy.visitSearch("awa");
    cy.wait(8000);
    cy.get("[data-cy='definitionTitle']").should("contain", "awa");

    cy.visitSearch("niya");
    cy.wait(8000);
    cy.get("[data-cy='definitionTitle']").should("contain", "niya");
  });

  // https://github.com/UAlbertaALTLab/morphodict/issues/176
  it("should show results for lexicalized diminutive forms", () => {
    cy.visitSearch("acâhkos");
    cy.wait(4000);
    cy.get("[data-cy='definitionTitle']").should("contain", "atâhk");
  });

  // https://github.com/UAlbertaALTLab/morphodict/issues/176
  describe("should show at least two lemmas for lexicalized diminutive forms", () => {
    it("should show atâhk and acâhkos for acâhkos", () => {
      cy.visitSearch("acâhkos");
      cy.wait(3000);
      cy.get('[data-cy=definitionTitle]')
        .should("contain", "atâhk")
        .and("contain", "acâhkos");
    });
  });

  // https://github.com/UAlbertaALTLab/morphodict/issues/181
  it("should just show three meanings for the lemma nipâw", () => {
    cy.visitSearch("nipâw");
    cy.wait(3000);
    cy.get('[data-cy=definitionTitle]');
    // check for length of 3
    for (let i = 1; i < 4; i++) {
      cy.get(`:nth-child(1) > .list-group > :nth-child(${i})`).should("exist");
    }
  });

  // https://github.com/UAlbertaALTLab/morphodict/issues/181
  it("should show the NRC logo", () => {
    cy.visit("/about");
    cy.wait(1000);
    cy.get(
      '[href^="https://nrc.canada.ca/en/research-development/research-collaboration/programs/canadian-indigenous-languages-technology-project"] > img'
    )
      .should("be.visible")
      .invoke("attr", "src")
  });

  it("should have the search bar appear wide on desktop", () => {
    let minimumWidth;
    const factor = 0.35; // it should be at least 35% the size of the viewport.
    cy.viewport("macbook-13"); // a small laptop size
    cy.visit("/");

    // Get the viewport width first...
    cy.window()
      .then((win) => {
        let viewportWidth = Cypress.$(win).width();
        minimumWidth = viewportWidth * factor;
      })
      .then(() => {
        cy.get('#search')
          .invoke("width")
          .should("be.greaterThan", minimumWidth);
      });
  });

  /**
   * See: https://github.com/UAlbertaALTLab/morphodict/issues/277
   */
  it("should show 3Sg→1Sg,2Sg rather than 4Sg/Pl→3Sg in the basic VTA layout", function () {
    // Go to a VTA word:
    cy.visitSearch("wâpamêw");
    cy.wait(4000);
    cy.contains("a", "wâpamêw").click();
    cy.wait(18000);

    // N.B.: This test will fail if the labels change. ¯\_(ツ)_/¯
    cy.contains("th", "s/he → him/her/them"); // 3Sg → 4Sg/PlO (lemma)
    cy.contains("th", "s/he → me"); // 3Sg → 1Sg
    cy.contains("th", "s/he → you"); // 3Sg → 2Sg
    cy.contains("th", "s/he/they → him/her"); // 4Sg/Pl → 3Sg
  });

  /**
   * Ensure search can be initiated from about page.
   *
   * See: https://github.com/UAlbertaALTLab/morphodict/issues/280
   */
  it("should search from the about page", function () {
    cy.visit("/about");
    cy.wait(3000);

    cy.search("acâhkos");
    cy.wait(4000);

    cy.url().should("contain", "/search");
    cy.get("[data-cy=definitionTitle]").should("contain", "atâhk");
  });

  /**
   * Ensure English names with capitalization gets matches
   *
   * See: https://github.com/UAlbertaALTLab/morphodict/issues/343
   */
  it("should present results when one searches with capitalized English names", function () {
    cy.visitSearch("Cree");
    cy.wait(10000);
    cy.get("[data-cy=searchResults]").should("be.visible");

    cy.visitSearch("Edmonton");
    cy.wait(5000);
    cy.get("[data-cy=searchResults]").should("be.visible");
  });

  /**
   * Ensure preverbs don't get weird search results
   *
   * See: https://github.com/UAlbertaALTLab/morphodict/issues/355
   */
  it("should not present un-related translation for preverbs", function () {
    cy.visitSearch("nitawi-");
    cy.wait(3000);

    // there should be only one result
    cy.get("[data-cy=searchResults]").first().should("contain", "go and");
  });

  /**
   * Ensure inflected form ê-kîsikâk get recognized
   *
   * See: https://github.com/UAlbertaALTLab/morphodict/issues/190
   */
  it("should not present un-related translation for preverbs", function () {
    cy.visitSearch("ê-kîsikâk");
    cy.wait(4000);

    // there should be only one result
    cy.get("[data-cy=searchResults]").should("contain", "kîsikâw");
  });

  /**
   * Ensure homographic entries can have paradigms shown
   *
   * See: https://github.com/UAlbertaALTLab/morphodict/issues/395
   */
  it("should let the user see the paradigm for different entries of ayâw and nôhtêpayiw", function () {
    // ayâw has three entries of different inflectional categories and nôhtêpayiw has two
    // With the bug,
    // when the user clicks on the lemmas some of them redirects the user to the same page, which appears like
    // the website didn't do anything

    cy.visitSearch("ayâw");
    cy.wait(3000);
    cy.get("[data-cy=lemmaLink]")
      .its("length")
      .then((length) => {
        // each clickable link should show paradigm
        for (let i = 0; i < length; i++) {
          cy.visitSearch("ayâw");
          cy.wait(3000);
          // .eq(n) selects the nth matched element
          cy.get("[data-cy=lemmaLink]").eq(i).click();
          cy.wait(15000);
          cy.get("[data-cy=paradigm]").should("be.visible");
        }
      })
      .then(() => {
        // repeat the same test with nôhtêpayiw
        cy.visitSearch("nôhtêpayiw");
        cy.wait(3000);
        cy.get("[data-cy=lemmaLink]")
          .its("length")
          .then((length) => {
            for (let i = 0; i < length; i++) {
              cy.visitSearch("nôhtêpayiw");
              cy.wait(3000);
              cy.get("[data-cy=lemmaLink]").eq(i).click();
              cy.wait(5000);
              cy.get("[data-cy=paradigm]").should("be.visible");
            }
          });
      });
  });

  /**
   * Ensure vowel length does not destroy affix search
   *
   * See: https://github.com/UAlbertaALTLab/morphodict/issues/420
   */
  it("should show affix search results when the query has diacritics on it", function () {
    // test assumption: without vowel length, affix search works
    cy.visitSearch("niso-");
    cy.wait(8000)
    cy.get("[data-cy=searchResults]").should("contain", "nîso-kîsikâw");

    // Now if we add the vowel length, we should still get the result
    cy.visitSearch("nîso-");
    cy.wait(8000);
    cy.get("[data-cy=searchResults]").should("contain", "nîso-kîsikâw");
  });

  /**
   * There should be symbols for pronouns and preverbs.
   *
   * See: https://github.com/UAlbertaALTLab/morphodict/issues/489
   */
  context("symbols also for pronouns and preverbs", function () {
    // TODO: add emoji to represent ôma/awa words
    const testCases = [
      ["niya", "null", "like: awa"],
      // ["ôma", "null️", "like: ôma"],   // This test is not currently working, but the behaviour is as expected
      ["nitawi-", "⚡️", "like: pê-"],
    ];

    for (const [wordform, emoji, inflectsLike] of testCases) {
      it(`should have a symbol for ${wordform}`, function () {
        cy.visitSearch(wordform);
        cy.wait(6000);

        cy.contains("[data-cy=elaboration]", inflectsLike).should(
          "contain",
          emoji
        );
      });
    }
  });

  /**
   * Ensure homographic entries can have paradigms shown
   *
   * See: https://github.com/UAlbertaALTLab/morphodict/issues/395
   */
  context("results for common place names", function () {
    const testCases = [
      ["Calgary", "otôskwanihk"],
      ["Regina", "oskana kâ-asastêki"],
      ["Saskatoon", "misâskwatôminihk"],
    ];

    for (const [englishName, creeName] of testCases) {
      it(`should have a definition for ${englishName}`, function () {
        cy.visitSearch(englishName.toLowerCase());
        cy.wait(5000);

        cy.contains("[data-cy=lemmaLink]", creeName);
      });
    }
  });

  it("should remove the word detail pages when viewing details then going to search", () => {
    // Visit the details page of one entry:
    cy.visitLemma("kotiskâwêw");
    cy.wait(6000);
    cy.contains(".definition-title", "kotiskâwêw");

    // Now, start searching for a completely DIFFERENT word
    cy.search("oskana");
    cy.wait(3000);
    // It should not exist
    cy.contains(".definition-title", "kotiskâwêw").should("not.exist");
  });
});
