/**
 * Test how citations should work in crkeng (itwêwina Plains Cree
 * dictionary).
 */
describe("Source citations", function () {
  const LEMMA_WITH_MD_AND_CW_CITATIONS = "nipâw";
  const SOURCES = ["MD", "CW"];
  const CRITICAL_INFORMATION = {
    MD: "Maskwacîs Dictionary",
    CW: "Cree: Words",
  };

  context("Search page", () => {
    for (let sourceAbbreviation of SOURCES) {
      it(`should cite on the search page, with a tooltip for ${sourceAbbreviation}`, () => {
        cy.visitSearch(LEMMA_WITH_MD_AND_CW_CITATIONS);
        cy.wait(3000);


        searchResult().contains(sourceAbbreviation).first().click();

        tooltip()
            .should("be.visible")
            .contains(CRITICAL_INFORMATION[sourceAbbreviation]);
      });
    }

    function searchResult() {
      return cy.get("#results").first();
    }
  });

  context("Details page", () => {
      for (let sourceAbbreviation of SOURCES) {
        it("should cite on the details page with a tooltip", () => {
          cy.visitLemma(LEMMA_WITH_MD_AND_CW_CITATIONS);
          cy.wait(7000);

          cy.get("[data-cy=meanings]")
              .contains(sourceAbbreviation)
              .first()
              .click();

          tooltip()
              .should("be.visible")
              .contains(CRITICAL_INFORMATION[sourceAbbreviation]);
        });
      }
  });

  function tooltip() {
    return cy.get('.tooltip-inner');
  }
});
