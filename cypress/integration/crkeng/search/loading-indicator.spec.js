context("Searching", () => {
  describe("Loading indicator", () => {
    beforeEach(() => {
      cy.visit("/");
    });

    it("should display a loading indicator", () => {
      cy.search("amisk");

      // The loading indicator should be visible!
      cy.get(".spinner-grow").should("be.visible");

      // Wait for the results to come back
      cy.wait(3000);
      cy.get("#results").should("be.visible");
    });

    it("should display an error indicator when loading fails", () => {
      // A fake word that should return 0 results
      cy.search("amitonan")

      // The loading indicator should be visible!
      cy.get(".spinner-grow").should("be.visible");

      // Wait for the results to come back
      cy.wait(3000);
      cy.get(".alert-heading")
        .should("be.visible");
    });
  });
});
