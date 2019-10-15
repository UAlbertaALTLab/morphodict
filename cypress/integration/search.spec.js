context('Searching', () => {
  describe('I want to know what a Cree word means in English', () => {
    // TODO: Enable this test when this issue is fixed:
    // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/120
    it.skip('should search for an exact lemma', () => {
      cy.visit('/')
      cy.get('[data-cy=search]')
        .type('acâhkos')

      cy.get('[data-cy=search-results]')
        .should('contain', 'star')
    })

    it('should perform the search by going directly to the URL', () => {
      cy.visit('/search/amisk')

      cy.get('[data-cy=search-results]')
        .should('contain', 'beaver')
    })
  })
})
