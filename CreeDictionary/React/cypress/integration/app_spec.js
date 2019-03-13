/// <reference types="Cypress" />
describe("Django REST framework / React quickstart app", () => {
         before(() => {
                cy.exec("npm run dev");
                cy.exec("npm run flush");
                });
         it("Search Area show up", () => {
            cy.visit("/");
            cy.get("form").submit();
            });
         // more tests here
         });
