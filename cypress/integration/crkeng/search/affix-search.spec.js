context("Searching", () => {
  context("Affix search", () => {
    it("should do prefix search and suffix search for Cree", () => {
      cy.visitSearch("nipaw");
      cy.wait(3000);
      cy.searchResultsContain("nipawâkan")
        .searchResultsContain("mâci-nipâw");
    });

    it("should do prefix search for English", () => {
      cy.visitSearch("sleep");
      cy.wait(3000);
      cy.searchResultsContain("sleeping");
    });

    it("should do suffix search for English", () => {
      cy.visitSearch("katoon");
      cy.wait(3000);
      cy.searchResultsContain("Saskatoon");
    });
  });
});
