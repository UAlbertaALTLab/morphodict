context('Regressions', () => {
  it('should handle a non-ASCII letter in the URL properly', () => {
    cy.visit('/search/acâhkos')

    cy.get('[data-cy=search-results]')
      .should('contain', 'acâhkos')
  })
})
