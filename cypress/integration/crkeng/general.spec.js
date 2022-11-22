/**
 * General tests about the website's behaviour as a regular website.
 */
context("General", function () {
  beforeEach(function () {
    cy.visit("/");
  });

  describe("Visiting the home page", () => {
    it("should say “itwêwina” in the header", () => {
      cy.get("h1").should("be.visible").should("contain", "itwêwina");
    });

    it("should greet the users in the content", () => {
      cy.get("main")
        .contains("h1, h2", /\bt[âā]n[i']?si\b/)
        .should("be.visible");
    });
  });

  describe("I want see all written Cree in Western Cree Syllabics", function () {
    it("should be accessible from the language selector", function () {
      cy.get("[data-cy=settings-menu]")
        // this should be `.type('{enter}')` but that mysteriously fails when
        // running cypress against firefox on Ubuntu, even though pressing enter
        // in the browser *does* work. Workaround is to click() instead.
        .click();

      cy.get("[data-cy=orthography-choices]")
        .should("be.visible")
        .contains("Syllabics")
        .click();
      cy.wait(1000);

      cy.get("h1").contains("ᐃᑘᐏᓇ");
    });
  });

  describe("I want to search for complex Cree words", function () {
    // See: https://github.com/UAlbertaALTLab/morphodict/issues/150
    it("should have a clickable example on the front page", function () {
      const word = "ê-kî-nitawi-kâh-kîmôci-kotiskâwêyâhk";

      cy.visit("/");

      cy.get("[data-cy=long-word-example]").should("contain", word).click();
      cy.wait(5000);

      // we should be on a new page.
      cy.url().should("contain", "/search");

      cy.get("[data-cy=lemmaLink]").should("contain", word);
    });
  });
});
