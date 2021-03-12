const { join } = require('path');

context('Admin interface', () => {
  it('should redirect anonymous users to the login page', function() {
    cy.visit('/admin')
    cy.location().should('match', /\/admin\/login\//)
  })

  function login() {
    cy.visit('/admin')
    cy.readFile(join(__dirname, '..', '..', 'CreeDictionary', '.cypress-user.json')).then(cypressUser => {
      cy.get('#id_username').type(cypressUser.username)
      cy.get('#id_password').type(cypressUser.password)
      cy.get('.submit-row > input').click()
    })
    cy.location('pathname').should('eq', '/admin/')

  }

  it('should allow login', function() {
    login()
  })

  it('should show auto-translations to logged-in users', function() {
    login()
    cy.visitSearch('acâhkosa')
    cy
      .get('[data-cy=search-result]').contains('little star over there')
      .get('.cite-dict').contains('auto')
  })

  it('should not show auto-translations to anonymous users', function() {
    cy.visitSearch('acâhkosa')
    cy.get('[data-cy=search-result]').each(r => {
      // Every result should have a dictionary citation
      cy.wrap(r).get('.cite-dict').should('have.length.at.least', 1)
        .each(citation => {
          // But none of those should be ‘auto’
          cy.wrap(citation).should('not.contain', 'auto')
        })
    })
  })
})

