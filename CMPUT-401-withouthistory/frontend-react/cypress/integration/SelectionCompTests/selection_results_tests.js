// selection_cmp_right_item_count.js created with Cypress
// The edmonton CW thing is an issue with the test data not with the site itself.

describe("Checks if we return something to the screen", () => {
  it("shows connected data points", () => {
    cy.visit("http://10.2.10.152/search/?q=amisk");
    cy.contains("amisk");
    cy.contains("amiskwaciy-wâskahikan");
  });
});

describe("Checks if we return something to the screen", () => {
  it("Shows that the first def contains the right words", () => {
    cy.visit("http://10.2.10.152/search/?q=amisk");
    cy.contains("beaver");
  });
});

describe("Checks if we return something to the screen", () => {
  it("Shows that the second word def contains the right words", () => {
    cy.visit("http://10.2.10.152/search/?q=amisk");
    cy.contains("Edmonton");
  });
});
