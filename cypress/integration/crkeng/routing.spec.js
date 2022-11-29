// if I click this or visit that, xxx should show

// corresponding requirements: https://github.com/UAlbertaALTLab/morphodict/issues/143
describe("urls for lemma detail page should be handled correctly", () => {
  it("should show lemma detail (paradigms) if a unambiguous url is given", function () {
    // Get to the definition/paradigm page for "wâpamêw"
    cy.visit("/word/wâpamêw/");
    cy.wait(25000);
    cy.get('.row > :nth-child(1)')
      .should("be.visible")
        .click()
    cy.get(':nth-child(1) > .card > .MuiPaper-root > .MuiCollapse-root > .MuiCollapse-wrapper > .MuiCollapse-wrapperInner > #panel1a-content > .MuiAccordionDetails-root > [style="width: 100%;"] > .card-body')
      .should("contain", "kiwâpamitin");
  });

  it("should redirect to search page if no match is found", function () {
    // acimonân is a fictional word
    let fakeWord = "acimonân";
    cy.visit(`/word/${fakeWord}/`);
    cy.get("[data-cy=paradigm]").should("not.exist");

    // test if the redirection happens
    cy.location().should((loc) => {
      expect(loc.pathname).to.eq("/search/");
      expect(loc.search).to.eq(`?q=${encodeURIComponent(fakeWord)}`);
    });

    // wrong slug disambiguator n is supplied, nipâw is a verb
    cy.visit("/word/nipâw@n");
    cy.get("[data-cy=paradigm]").should("not.exist");

    // test if the redirection happens
    cy.location().should((loc) => {
      expect(loc.pathname).to.eq("/search/");
      expect(loc.search).to.eq(`?q=${encodeURIComponent("nipâw")}`);
    });
  });

  it("should redirect to search page if the lemma_text in /word/lemma_text matches multiple results", function () {
    // pipon is a verb as well as a noun
    cy.visit("/word/pipon/");
    cy.get("[data-cy=paradigm]").should("not.exist");

    // test if the redirection happens
    cy.location().should((loc) => {
      expect(loc.pathname).to.eq("/search/");
      expect(loc.search).to.eq("?q=pipon");
    });
  });

  it("should add relevant constraints as query params in href for ambiguous lemmas on the search page", function () {
    // pipon is a verb as well as a noun
    cy.visitSearch("pipon");
    cy.wait(5000);

    let lemmaUrls = [];

    // both results should be present
    cy.get("[data-cy=lemmaLink]")
      .each(($e) => {
        lemmaUrls.push($e.attr("href"));
      })
      .then(() => {
            console.log(lemmaUrls);
            expect(lemmaUrls)
                .to.include("/word/pipon@ni")
                .and.to.include("/word/pipon@vii");
          }
      );
  });
});
