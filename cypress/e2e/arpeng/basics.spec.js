import urls from "../../support/urls";

describe("The Arapaho site", function () {
  it("works", function () {
    cy.visit(`${urls.arpeng}`);
    cy.get(".branding__heading").contains("Arapaho Dictionary");
  });

  it("can search for a word", function () {
    cy.visitSearch(`nihooyoo`, urls.arpeng).searchResultsContain("níhooyóó-");
  });

  it("can display a paradigm", function () {
    cy.visit(`${urls.arpeng}/word/níhooyóó-`);
    cy.get(".paradigm-cell").contains("hoownihooyoono");
  });
});
