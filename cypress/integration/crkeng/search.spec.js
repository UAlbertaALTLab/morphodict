context("Searching", () => {
  describe("I want to know what a Cree word means in English", () => {
    // https://github.com/UAlbertaALTLab/morphodict/issues/120
    it("should search for an exact lemma", () => {
      cy.visitSearch("minos")
      cy.wait(8000);
      cy.searchResultsContain("cat");
    });
  });

  describe("search results should be ranked by modified levenshtein distance", () => {
    it("should show nipîhk before nîpîhk if the search string is the former", () => {
      cy.visitSearch("nipîhk");
      cy.wait(2000);

      cy.get('.app__content > :nth-child(1) > :nth-child(1) > :nth-child(1)')
        .should("contain", "nipîhk")
        .and("contain", "water");
    });
  });

  describe("As an Administrator, I want to integrate words from multiple dictionary sources.", () => {
    it("should display the dictionary source on the page", () => {
      // atâhk should be defined, both in the CW dictionary and the MD
      // dictionary:
      let lemma = "atâhk";
      let dicts = ["CW", "MD"];

      cy.visitSearch(lemma);
      cy.wait(2000);
      cy.get('[data-cy=citation]')
        .as("definition");

      // Check each citation.
      for (let id of dicts) {
        cy.get("@definition")
          .contains(id)
          .should("be.visible")
          .should(($cite) => {
            expect($cite.text()).to.match(/^\s*\w+\s*$/);
          });
      }
    });
  });

  describe("I want the search for a Cree word to tolerate a query which may be spelled in a non-standard or slightly incorrect way.", () => {
    it("should treat apostrophes as short-Is ", () => {
      cy.visit("/");

      cy.visitSearch("tan'si");
      cy.wait(2000);
      cy.searchResultsContain("tânisi");
    });

    it("should forgive omitted long vowel marking", () => {
      cy.visit("/");

      cy.visitSearch("acimew");
      cy.wait(2000);
      cy.searchResultsContain("âcimêw");

      cy.clearSearchBar();

      cy.visitSearch("ayiman");
      cy.wait(2000);
      cy.searchResultsContain("âyiman");
    });

    it("should handle English-influenced spelling", () => {
      cy.visitSearch("atchakosuk");
      cy.wait(2000);
      cy.searchResultsContain("atâhk");
    });
  });

  describe("I want to see the normatize form of my search", () => {
    it("should search the normatized form of the matched search string", () => {
      // *nipe-acimon == nipê-âcimon == PV/pe+âcimow+V+AI+Ind+1Sg
      const searchTerm = "nipe-acimon";
      cy.visit("/");

      cy.visitSearch(searchTerm);
      cy.wait(3000);

      cy.get('[data-cy=all-search-results]')
        .first()
        .as("searchResult");

      // normatized form:
      cy.get("@searchResult").contains(
        "[data-cy=definitionTitle]",
        "nipê-âcimon"
      );

      cy.get("@searchResult")
        .contains("âcimow");
    });
  });

  it("should leave out not normatized content", () => {
    // nipa means "Kill Him" in MD
    cy.visitSearch("nipa");
    cy.wait(8000);
    cy.searchResultsContain("sleeps")
      .and("not.contain", "Kill");
  });

  describe("When I perform a search, I should see the 'info' icon on corresponding entries", () => {
    // Right – this is the test for issue #239 (https://github.com/UAlbertaALTLab/morphodict/issues/239).

    // At present, I want to target the definition's title, then look at the children to see if the the 'i' icon is
    // there. There's probably a more elegant way to do this but I think that'll come as I become more comfortable with the codebase.
    it("should show the 'info' icon to allow users to access additional information", () => {
      // borrowed the following four lines from above and used 'nipaw' for testing purposes.
      const searchTerm = "niya";
      cy.visitSearch(searchTerm);
      cy.wait(8000);

      cy.get('[data-cy=infoButton]').first().click();
      cy.get('[data-cy=infoButtonInfo]').should('be.visible');
    });
  });

  describe("A tooltip should show up when the user click/focus on the i icon beside the matched wordform", () => {
    it("should show tooltip when the user focuses on the i icon beside ê-wâpamat", () => {
      cy.visitSearch("ewapamat");
      cy.wait(2000);

      // not visible at the start
      cy.get("[data-cy=infoButtonInfo]")
        .should("not.exist");


      cy.get("[data-cy=infoButton]").first().click();

      cy.get("[data-cy=infoButtonInfo]").should("be.visible").and("contain", "Action word"); // verb
    });

    it("should show tooltip with relevant linguistic breakdowns when the user clicks on the i icon beside ê-wâpamat", () => {
      cy.visitSearch("ewapamat");
      cy.wait(2000);

      // not visible at the start
      cy.get("[data-cy=infoButtonInfo]")
        .should("not.exist");

      // has to use force: true since div is not clickable
      cy.get("[data-cy=infoButton]").first().click();

      cy.get("[data-cy=infoButtonInfo]")
        .should("be.visible")
        // NOTE: this depends on Antti's relabellings; if they change,
        // this assertion has to change :/
        .and("contain", "Action word — like") // VTA
        .and("contain", "you (one) → him/her"); // 3Sg -> 4Sg/PlO
    });

    it("should show linguistic breakdowns as an ordered list when the user clicks on the i icon beside a word", () => {
      cy.visitSearch("nipaw");
      cy.wait(2000);

      // tab through the elements to force the tooltip to pop up
      cy.get("[data-cy=infoButton]").first().click();

      // see the linguistic breakdown as an ordered list
      cy.get("[data-cy=infoButtonInfo]").contains("Action word");
    });

    it("should allow the tooltip to be focused on when the user tabs through it", () => {
      // goodness, that's a mouthful and should _probably_ be worded better.
      // begin from the homepage
      cy.visit("/");
      cy.search("nipaw");
      cy.wait(2000);

      // tab through the page elements until arriving on the '?' icon
      cy.get("[data-cy=infoButton]").first().click();

      // it should trigger the focus icon's outline's focused state
      cy.get("[data-cy=infoButton]")
        .first()
        .focus()
        .should("have.css", "outline");
    });

    it("should not overlap other page elements when being displayed in the page", () => {
      // Eddie's comment used a very long word in `e-ki-nitawi-kah-kimoci-kotiskaweyahk`, so we will use that!
      cy.visitSearch("e-ki-nitawi-kah-kimoci-kotiskaweyahk");
      cy.wait(3000);

      // force the tooltip to appear
      cy.get("[data-cy=infoButton]").first().click({ force: true });

      // check that the z-index of the tooltip is greater than that of all other page elements
      cy.get("[data-cy=infoButton]")
        .first()
        .focus()
    });

    /**
     * https://github.com/UAlbertaALTLab/morphodict/issues/549
     * Can't get this one passing right now :_(
     */
    it("displays the stem prominently in the linguistic breakdown", function () {
      cy.visitSearch("pê-nîmiw");
      cy.wait(2000);

      // Open the linguistic breakdown popup
      cy.get("[data-cy=infoButton]")
        .first()
        .click();

      cy.get("[data-cy=infoButtonInfo]")
        .as("linguistic-breakdown")
        .should("be.visible");

      cy.get("@linguistic-breakdown")
        .contains("nîmi-")
        .should(($el) => {
          expect(+$el.css("font-weight")).to.be.greaterThan(380);
        });
    });

    it("displays the suffix features in the linguistic breakdown", function () {
      cy.visitSearch("pê-nîmiw");
      cy.wait(2000);

      // Open the linguistic breakdown popup
      cy.get("[data-cy=infoButton]")
        .first()
        .click();

      cy.get("[data-cy=infoButtonInfo]")
        .as("linguistic-breakdown")
        .should("be.visible");
      cy.get("@linguistic-breakdown").contains("Action word");
      cy.get("@linguistic-breakdown").contains("ni-/ki- word");
      cy.get("@linguistic-breakdown").contains("s/he");
    });
  });

  describe("When results are not found", function () {
    const NON_WORD = "acimonân";

    it("should report no results found for ordinary search", function () {
      cy.visitSearch(NON_WORD);
      cy.wait(2000);

      cy.location().should((loc) => {
        expect(loc.pathname).to.eq("/search/");
        expect(loc.search).to.contain(`q=${encodeURIComponent(NON_WORD)}`);
      });

      // There should be something telling us that there are no results
      cy.get('.alert-heading')
        .and("contain", "No results found")
        .should("contain", NON_WORD);
    });

    it("should report no results found when visiting the page directly", function () {
      cy.visitSearch(NON_WORD);
      cy.wait(1000);

      cy.get('.alert-heading')
        .and("contain", "No results found")
        .should("contain", NON_WORD);
    });
  });

  describe("fancy queries", function () {
    it("should show search features for a verbose search", function () {
      cy.visitSearch("verbose:1 acahkosa");
      cy.wait(2000);

      cy.get("[data-cy=verbose-info]").should("contain", "relevance_score");
    });

    it("should show auto-translations with auto:y", function () {
      // NB: need to make sure this wordform is added **explicitly** in the
      // `ensuretestdb` management commands:
      cy.visitSearch("auto:y niminôsak");
      cy.wait(2000);
      cy.get("#results")
        .contains("my cats")
        .get(".cite-dict")
        .contains("🤖CW");
    });
  });
});
