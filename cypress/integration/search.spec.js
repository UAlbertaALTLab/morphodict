context('Searching', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  describe('I want to know what a Cree word means in English', () => {
    // TODO: Enable this test when this issue is fixed:
    // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/120
    it.skip('should search for an exact lemma', () => {
      // https://on.cypress.io/should
      cy.get('[data-cy=search]')
        .type('acâhkos')

      cy.get('[data-cy=search-results]')
        .should('contain', 'star')
    })
  })
})
