context("Searching", () => {
  describe("I want to see search results by the URL", () => {
    it("performs the search by going directly to the URL", () => {
      cy.visitSearch("minos");
      cy.wait(3000);
      cy.searchResultsContain("cat");
    });
  });

  describe("I want to have URL changed dynamically according to the page", function () {
    it("should display corresponding url", function () {
      cy.visit("/");
      cy.search("niya");
      cy.wait(3000);

      cy.location("pathname").should("contain", "/search");
      cy.location("search").and("contain", "q=niya");
    });

    it("should not change location upon pressing enter", function () {
      let originalPathname, originalSearch;
      cy.visit("/");

      cy.search("niya");
      cy.wait(3000);

      cy.location().should((loc) => {
        originalPathname = loc.pathname;
        originalSearch = loc.search;
        expect(loc.pathname).to.eq("/search/");
        expect(loc.search).to.contain("q=niya");
      });

      // Press ENTER!
      cy.get("#search").type("{Enter}");

      cy.location().should((loc) => {
        expect(loc.pathname).to.eq(originalPathname);
        expect(loc.search).to.eq(originalSearch);
      });
    });
  });
});
