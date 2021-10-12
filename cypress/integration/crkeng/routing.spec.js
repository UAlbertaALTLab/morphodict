// if I click this or visit that, xxx should show

// corresponding requirements: https://github.com/UAlbertaALTLab/morphodict/issues/143
describe("urls for lemma detail page should be handled correctly", () => {
  it("should show lemma detail (paradigms) if a unambiguous url is given", function () {
    // Get to the definition/paradigm page for "wâpamêw"
    cy.visit("/word/wâpamêw/");
    cy.get("[data-cy=paradigm]")
      .should("be.visible")
      .and("contain", "kiwâpamitin");
  });

  it("should redirect to search page if no match is found", function () {
    // pîpîpôpô is a fictional word
    let fakeWord = "pîpîpôpô";
    cy.visit(`/word/${fakeWord}/`);
    cy.get("[data-cy=paradigm]").should("not.exist");

    // test if the redirection happens
    cy.location().should((loc) => {
      expect(loc.pathname).to.eq("/search");
      expect(loc.search).to.eq(`?q=${encodeURIComponent(fakeWord)}`);
    });

    // wrong slug disambiguator n is supplied, nipâw is a verb
    cy.visit("/word/nipâw@n");
    cy.get("[data-cy=paradigm]").should("not.exist");

    // test if the redirection happens
    cy.location().should((loc) => {
      expect(loc.pathname).to.eq("/search");
      expect(loc.search).to.eq(`?q=${encodeURIComponent("nipâw")}`);
    });
  });

  it("should redirect to search page if the lemma_text in /word/lemma_text matches multiple results", function () {
    // pipon is a verb as well as a noun
    cy.visit("/word/pipon/");
    cy.get("[data-cy=paradigm]").should("not.exist");

    // test if the redirection happens
    cy.location().should((loc) => {
      expect(loc.pathname).to.eq("/search");
      expect(loc.search).to.eq("?q=pipon");
    });
  });

  it("should add relevant constraints as query params in href for ambiguous lemmas on the search page", function () {
    // pipon is a verb as well as a noun
    cy.visitSearch("pipon");

    let lemmaUrls = [];

    // both results should be present
    cy.get("[data-cy=definition-title] a")
      .each(($e) => {
        lemmaUrls.push($e.attr("href"));
      })
      .then(() =>
        expect(lemmaUrls)
          .to.include("/word/pipon@n/")
          .and.to.include("/word/pipon@v/")
      );
  });
});
