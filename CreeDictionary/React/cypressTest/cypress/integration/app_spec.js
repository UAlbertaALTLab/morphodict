/// <reference types="Cypress" />
describe("Django REST framework / cree intelligent dictionary app", () => {
   // Currently using...
   //       word: mitâs 
   //       width of screen: 1400pixel
   //       height of screen: 900pixel
   // for testing
   const state = {
      word: "mitâs",
      wordLanguage: "Cree",
      wordCategory: "Noun",
      height: 900,
      width: 1400,
   };
   //Connect to the web
   before(() => {
      cy.exec("npm run dev");
      cy.viewport(state.width, state.height)
   });
   beforeEach(() => {
      cy.fixture("cree/creeWordSearch").as("cree");
    });
   //Test for Search form
   it("Search Area show up", () => {
      cy.visit("/");
      cy.get(".sidebar").should("be.visible");
      cy.get("form").should("be.visible");
      cy.get("input").should("have.value", "Enter Word");
      cy.get("input").type(this.cree.word).should("have.value", this.cree.word);
   });
   //Test for return when serch word
   it("List the search result", () => {
      //cy.get("input").type(this.cree.word);
      //cy.get("#Search").submit();
      //cy.wait(5000)
      //cy.get(".card-title");
   });
   //Test for detail of selected word
   it("Onclick on word and gains detail", () => {
      //cy.get("li").contains(state.word + " | " + state.wordLanguage + " | " + state.wordCategory).click();
      cy.get("h1")
   });
   // more tests here
   // The tests for layout, cree language, eng->cree, and cree->eng, backward and forward button will be added by sprint 4
});
