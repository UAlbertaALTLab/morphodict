context("The Legend page", function () {
  describe("Visiting any page", () => {
    it("should have a link to the about page in the footer", () => {
      cy.visit("/");
      cy.get("footer").contains("a", "Legend").click();

      cy.url().should("contain", Cypress.env("legend_url"));
    });
  });

  describe("Visiting the legend page", () => {
    beforeEach(function () {
      cy.visit(Cypress.env("legend_url"));
    });

    it("should have a title", () => {
      cy.get("main").contains("h2", /\bLegend/i);
    });

    const AROKS_ABBREVIATIONS = ["s.t.", "s.o.", "s/he"];
    for (const abbrv of AROKS_ABBREVIATIONS) {
      it(`should define ${abbrv}`, () => {
        cy.get("main").contains("dt", abbrv).next().should("match", "dd");
      });
    }
  });
});
