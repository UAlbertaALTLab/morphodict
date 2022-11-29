/**
 * Similar to ./result-header.spec.js -- displays more data
 */
context("Searching", () => {
  before(() => setDefaultDisplayMode());
  after(() => setDefaultDisplayMode());

  // See: https://github.com/UAlbertaALTLab/morphodict/issues/445#:~:text=4.%20Inflected%20form
  context("result header", function () {
    const lemma = "mîciw";
    const inflectionalClass = "VTI-3";

    it("shows the inflectional class in linguistic mode", function () {
      cy.visitSearch(lemma);
      cy.wait(4000);

      inflectionalClassInDefinitionTitle().should("not.exist");

      cy.get("[data-cy=enable-linguistic-mode-long]").click();

      cy.get("main")
        .contains(inflectionalClass)
        .should("be.visible");
    });

    function inflectionalClassInDefinitionTitle() {
      return cy.get(
        "[data-cy=matched-wordform]:first [data-cy=inflectional-class]"
      );
    }
  });

  describe("FST analysis", () => {
    // See: https://github.com/UAlbertaALTLab/morphodict/issues/742
    it("should display in Plain English", () => {
      cy.visitSearch("nimaskomak");
      cy.wait(3000);

      // Open the linguistic breakdown popup
      cy.get("[data-cy=infoButton]:first")
        .click();

      cy.get("[data-cy=infoButtonInfo]:first")
          .should("contain", "Naming word")
          .and("contain", "my")
          .and("contain", "many");

    });

    it("should display in Linguistic English", () => {
      cy.visit("/");
      cy.get("[data-cy=enable-linguistic-mode-long]").click();

      cy.visitSearch("nimaskomak");
      cy.wait(3000);

      // Open the linguistic breakdown popup
      cy.get("[data-cy=all-search-results]:first")
        .find("[data-cy=infoButton]:first")
        .click();

      cy.get("[data-cy=infoButtonInfo]:first")
        .should("be.visible")
        .then(($popup) => {
          let popupText = $popup.text().toLowerCase().replace(/\s+/, " ");

          expect(popupText).to.contain("noun");
          expect(popupText).to.contain("animate");
          expect(popupText).to.contain("1st person");
          expect(popupText).to.contain("plural");
        });
    });
  });

  function setDefaultDisplayMode() {
    cy.visit("/");
    cy.wait(1000);
    cy.get("[data-cy=enable-community-mode]").click();
  }
});
