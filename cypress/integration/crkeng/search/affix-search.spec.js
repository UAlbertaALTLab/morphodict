context("Searching", () => {
  context("Affix search", () => {
    it("should do prefix search and suffix search for Cree", () => {
      cy.visitSearch("nipaw")
        .searchResultsContain("nipawâkan")
        .searchResultsContain("mâci-nipâw");
    });

    it("should do prefix search for English", () => {
      cy.visitSearch("sleep").searchResultsContain("sleeping");
    });

    it("should do suffix search for English", () => {
      cy.visitSearch("katoon").searchResultsContain("saskatoon");
    });
  });
});
