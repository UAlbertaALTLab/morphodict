context("Searching", () => {
  describe("I want to see search results showing dynamically while I type", () => {
    // https://github.com/UAlbertaALTLab/morphodict/issues/120
    it("should search for first minos, then minosis", () => {
      cy.visit("/");
      cy.search("minos");
      cy.wait(3000);
      cy.searchResultsContain("cat");

      // makes it minos+is = minosis
      cy.search("is");
      cy.wait(3000);
      cy.searchResultsContain("kitten");
    });
  });

  describe("I want to see search results showing immediately after pressing enter", () => {
    // https://github.com/UAlbertaALTLab/morphodict/issues/120
    it("shows results for minosis immediately after enter is pressed", () => {
      cy.visit("/");
      cy.search("minosis", { pressEnter: true });
      cy.wait(3000);
      cy.searchResultsContain("kitten");
    });
  });
});
