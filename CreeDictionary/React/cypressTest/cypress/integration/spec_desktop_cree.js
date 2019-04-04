/// <reference types="Cypress" />
describe("Django REST framework / cree intelligent dictionary app Desktop Ver cree->eng", () => {
   // Currently using...
   //       word: mitâs 
   //       width of screen: 1400pixel
   //       height of screen: 900pixel
   // for testing
   const state = {
      height: 900,
      width: 1400,
   };
   //Connect to the web
   before(() => {
      cy.exec("npm run dev");
      cy.viewport(state.width, state.height)
      cy.viewport(state.width, state.height);
   });
   beforeEach(() => {
      cy.fixture("/cree/creeWordSearch.json").as("cree");
   });
   //Test for Search form
   it("Search Area show up", () => {
      cy.visit("/");
      cy.get(".sidebar").should("be.visible");
      cy.get("form").should("be.visible");
      cy.get('@cree').then((cree) => {
         cy.get("input").type(cree.word).should("have.value", cree.word);
      })
   });
   //Test for return when search word
   it("List the search result", () => {
      cy.get("#Search").submit();
      cy.get("div div.col-lg-9 div.card").should("be.visible");
      cy.get('@cree').then((cree) => {
         cy.get("div div.col-lg-9")
            .get("div h3.card-header")
            .contains(cree.word)
            .should("be.visible");
      })
   });
   //Test for detail of selected word
   it("Onclick on word and gains detail", () => {
      cy.get('@cree').then((cree) => {
         cy.get("div div.col-lg-9")
            .get("div h3.card-header")
            .contains(cree.word)
            .click();
         cy.get(".table").should("not.be.visible");
         cy.get(".card-body h3").should("be.visible");
      })
   });
   //Test for table of selected word
   it("Onclick on arrow and shows table", () => {
      cy.get('@cree').then((cree) => {
         cy.get("#basic")
            .click()
            .get("#basictable")
            .should("be.visible");
         cy.get("#extended").click()
            .get("#basic .card-header").click()
            .get("#basictable")
            .should("not.be.visible")
            .get("#extendedtable")
            .should("be.visible");
      })
   });
   // more tests here
   // The tests for layout, cree language, eng->cree, and cree->eng, backward and forward button will be added by sprint 4
});
