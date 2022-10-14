// selection_cmp_right_item_count.js created with Cypress
// The edmonton CW thing is an issue with the test data not with the site itself.

describe("Checks if we return something to the screen", () => {
  it("shows connected data points", () => {
    cy.visit("http://localhost:3000/search/?q=amisk");
    cy.wait(3000);
    cy.contains("amisk");
    cy.contains("amiskwaciy-wâskahikan");
  });

  it("Shows that the first def contains the right words", () => {
    cy.visit("http://localhost:3000/search/?q=amisk");
    cy.wait(3000);
    cy.contains("beaver");
  });

  it("Shows that the second word def contains the right words", () => {
    cy.visit("http://localhost:3000/search/?q=amisk");
    cy.wait(3000);
    cy.contains("Edmonton");
  });
});
