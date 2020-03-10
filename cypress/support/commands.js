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

/**
 * Fixes a bug (feature?) in Cypress: it should call encodeURIComponent() for
 * /path/components/ in visit(). This way paths with non-ASCII stuff is
 * escaped automatically.
 *
 * Additional options:
 *
 *  escapeComponents: Boolean [default: true]  -- whether to escape URL components at all.
 */
Cypress.Commands.overwrite('visit', (originalVisit, url, options = {}) => {
  // Escape components by default:
  if (options.escapeComponents === undefined) {
    options.escapeComponents = true
  }

  let newURL
  if (options.escapeComponents) {
    newURL = url.split('/').map(encodeURIComponent).join('/')
  } else {
    newURL = url
  }
  delete options.escapeComponents

  if (newURL !== url) {
    Cypress.log({
      name: 'visit',
      message:`‼️  Rewriting ${url} -> ${newURL}`
    })
  }

  return originalVisit(newURL, options)
})

/**
 * Visit the search page for the given search query.
 */
Cypress.Commands.add('visitSearch', { prevSubject: false }, (searchQuery) => {
  Cypress.log({
    name: 'visitSearch',
    message: `visiting search page for: ${searchQuery}`
  })
  return cy.visit(`/search?q=${encodeURIComponent(searchQuery)}`, { escapeComponents: false })
})
