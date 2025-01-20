import urls from "../../support/urls";

describe("The Tsúūt'ínà site", function () {
  this.beforeEach(() => {
    const cookies = Cypress.env('cookies') || []
    cookies.forEach(c => cy.setCookie(c.name,c.value))
  });

  it("works", function () {
    cy.visit(`${urls.srseng}`);
    cy.get(".branding__heading").contains("Gūnáhà");
  });

  it("can login before anything", function () {
    cy.user_login(`${urls.srseng}/accounts/login/?next=/`)
    cy.getCookies().then(cookies => {
      var values=""
      cookies.forEach(c => values+=`{${c.name},${c.value}}`)
      Cypress.log({
        name: "cookies",
        message: `${values}`,
      })
      Cypress.env('cookies', cookies)
  })
  cy.visit(`${urls.srseng}`);
  });

  it("can search for a word", function () {
        cy.visitSearch(`yidiskid`, urls.srseng).searchResultsContain("yídiskid");
  });

  it("can display a paradigm", function () {
    cy.visit(`${urls.srseng}/word/yídiskid`);
    cy.get(".paradigm-cell").contains("mídiskid");
  }); 
});
