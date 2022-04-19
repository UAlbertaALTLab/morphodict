context("The Legend page", function () {
  describe("Visiting any page", () => {
    it("should have a link to the about page in the footer", () => {
      cy.visit("http://10.2.10.152/");
      cy.contains("Legend of abbreviations").click();

      cy.url().should("contain", "cree-dictionary-legend");
    });
  });

  describe("Visiting the legend page", () => {
    beforeEach(function () {
      cy.visit("http://10.2.10.152/cree-dictionary-legend");
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
