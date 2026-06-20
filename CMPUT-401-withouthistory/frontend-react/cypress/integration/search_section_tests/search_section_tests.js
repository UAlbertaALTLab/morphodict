// selection_cmp_right_item_count.js created with Cypress
// The edmonton CW thing is an issue with the test data not with the site itself.

describe("Checks if sections shows consonants", () => {
  it("shows whole response from amisk", () => {
    cy.visit("http://10.2.10.152/search/?q=amisk");
    cy.contains("Consonant-/w/ animate noun stem");
  });
});

describe("Checks if sections shows the right two orderings ", () => {
  it("shows two defs for amisk", () => {
    cy.visit("http://10.2.10.152/search/?q=amisk");
    cy.contains("1. Edmonton, AB :CW");
    cy.contains("2. Fort Edmonton :CW");
    cy.contains("1. beaver :CW");
  });
});
