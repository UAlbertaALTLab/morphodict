context("Searching", () => {
  describe("Loading indicator", () => {
    beforeEach(() => {
      cy.visit("/");
    });

    it("should display a loading indicator", () => {
      cy.intercept("**/_search_results/amisk", {
        body: `<ol><li data-cy="search-results">
            <span lang="cr">amisk</span>: beaver
        </li></ol>`,
        delayMs: 200,
      }).as("search");

      // We have typed all but ONE character of the search string:
      cy.get("[data-cy=search]").invoke("val", "amis").as("searchBox");

      // Initially, there should be no loading indicator visible
      cy.get("[data-cy=loading-indicator]").should("not.be.visible");

      // Type the last character of the search string, as normal:
      cy.get("@searchBox").type("k");

      // The loading indicator should be visible!
      cy.get("[data-cy=loading-indicator]").should("be.visible");

      // Wait for the results to come back
      cy.wait("@search");
      cy.get("[data-cy=loading-indicator]").should("not.be.visible");
    });

    it("should display an error indicator when loading fails", () => {
      cy.intercept("/_search_results/amisk", {
        statusCode: 500,
        body: "Internal Server Error!",
      }).as("search");

      // We have typed all but ONE character of the search string:
      cy.get("[data-cy=search]").invoke("val", "amis").as("searchBox");

      // Initially, there should be no loading indicator visible
      cy.get("[data-cy=loading-indicator]").should("not.be.visible");

      // Type the last character of the search string, as normal:
      cy.get("@searchBox").type("k");

      // The loading indicator should be visible!
      cy.get("[data-cy=loading-indicator]").should("be.visible");

      // Wait for the results to come back
      cy.wait("@search");
      cy.get("[data-cy=loading-indicator]")
        .should("be.visible")
        .should("have.class", "search-progress--error");
    });
  });
});
