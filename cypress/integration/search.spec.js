context('Searching', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  describe('I want to know what a Cree word means in English', () => {
    it('should search for an exact lemma', () => {
      // https://on.cypress.io/should
      cy.get('[data-cy=search]')
        .type('acâhkos')

      cy.get('[data-cy=search-results]')
        .should('contain', 'star')
    })
  })
})
