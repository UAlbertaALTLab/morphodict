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
  describe('Loading indicator', () => {
    beforeEach(() => {
      cy.server()
      cy.visit('/')
    })

    it('should display a loading indicator', () => {
      cy.route({
        url: '/_search_results/**',
        delay: 100, // milliseconds of delay
        response: `<ol><li data-cy="search-results">
            <span lang="cr">amisk</span>: beaver
        </li></ol>`
      }).as('search')

      cy.get('[data-cy=search]')
        .as('searchBox')

      // Initially, there should be no search results visible:
      cy.get('body')
        .not('[data-cy=search-results]')
      // We type our search, like normal:
      cy.get('@searchBox')
        .type('amisk')

      // This the loading indicator should be visible!
      cy.get('[data-loading-indicator]')
        .should('be.visible')

      // Wait for the results to come back
      cy.wait('@search')
      cy.get('[data-loading-indicator]')
        .should('not.be.visible')
    })
  })
})
