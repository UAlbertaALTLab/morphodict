context('Paradigms', () => {
  describe(' I want to search for a Cree word and see its inflectional paradigm', () => {
    it('should display the paradigm for an NA word', () => {
      cy.visit('/search/acâhkos')
      cy.get('[data-cy=search-results]')
        .contains('a', 'acâhkos')
        .click()

      cy.get('[data-cy=paradigm]')
        .as('paradigm')

      cy.get('@paradigm')
        .should('contain', 'acâhkos')
        .and('contain', 'acâhkosak')
        .and('contain', 'acâhkosa')
    })
  })
})
