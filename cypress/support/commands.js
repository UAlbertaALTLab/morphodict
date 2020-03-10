// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This is will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })

// fixes a bug (feature?) in Cypress: always encodeURIComponent in call to visit:
Cypress.Commands.overwrite('visit', (originalVisit, url, options) => {
  let newURL = url.split('/').map(encodeURIComponent).join('/')
  if (newURL !== url) {
    Cypress.log({
      name: 'visit',
      message:`‼️  Rewriting ${url} -> ${newURL}`
    })
  }

  return originalVisit(newURL, options)
})


Cypress.Commands.add('visitSearch', { prevSubject: false}, (searchTerm) => {
  Cypress.log({
    name: 'visitSearch',
    message: `visiting search page for: ${searchTerm}`
  })
  return cy.visit(`/search/${searchTerm}`)
})
