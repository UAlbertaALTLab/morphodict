/// <reference types="Cypress" />
describe("Django REST framework / cree intelligent dictionary app", () => {
   // Currently using...
   //       word: mitâs 
   // for testing
   const state = {
      word: "mitâs",
      wordLanguage: "Cree",
      wordCategory: "Noun",
   };
   //Connect to the web
   /*before(() => {
      cy.exec("npm run dev");
      //cy.exec("npm run flush");
   });*/
   //Test for Search form
   it("Search Area show up", () => {
      cy.visit("/React");
      cy.get("form");
   });
   //Test for return when serch word
   it("List the search result", () => {
      cy.get("input").type(state.word);
      cy.get("#Search").submit();
      cy.wait(5000)
      cy.get("li").should("contain", state.word);
   });
   //Test for detail of selected word
   it("Onclick on word and gains detail", () => {
      cy.get("li").contains(state.word + " | " + state.wordLanguage + " | " + state.wordCategory).click();
      cy.get("h1")
   });
   // more tests here
   // The tests for layout, cree language, eng->cree, and cree->eng, backward and forward button will be added by sprint 4
});
