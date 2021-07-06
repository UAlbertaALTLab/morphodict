context('The settings page', () => {
  it('should be accessible from the home page', () => {
    cy.visit('/')
    cy.get('[data-cy=settings-menu]')
      .click()
      .get('[data-cy=settings-link')
      .click()

    cy.location()
      .should('match', /\bsettings\b/)
  })
})
