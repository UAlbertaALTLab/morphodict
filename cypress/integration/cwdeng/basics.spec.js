import urls from "../../support/urls";

describe("The Woods Cree site", function () {
  it("works", function () {
    cy.visit(`${urls.cwdeng}`);
    cy.get(".branding__heading").contains("itwīwina");
  });

  it("can search for a word", function () {
    cy.visitSearch(`makes pottery`, urls.cwdeng).searchResultsContain(
      "asiskīwithākanihkīw"
    );
  });

  it("can display a paradigm", function () {
    cy.visit(`${urls.cwdeng}/word/asiskīwithākanihkīw`);
    cy.get(".paradigm-cell").contains("kitasiskīwithākanihkānaw");
  });
});
