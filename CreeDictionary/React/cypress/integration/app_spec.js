/// <reference types="Cypress" />
describe("Django REST framework / cree intelligent dictionary app", () => {
         before(() => {
                cy.exec("npm run dev");
                //cy.exec("npm run flush");
                });
         it("Search Area show up", () => {
            cy.visit("/React");
            cy.get("form").submit();
            });
         // more tests here
         });
