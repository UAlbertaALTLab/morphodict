context('Searching', () => {
  describe('Loading indicator', () => {
    beforeEach(() => {
      cy.server()
      cy.visit('/')
    })

    // TODO: implement workaround for fetch()
    it.skip('should display a loading indicator', () => {
      cy.route({
        url: '/_search_results/amisk',
        delay: 200, // milliseconds of delay
        response: `<ol><li data-cy="search-results">
            <span lang="cr">amisk</span>: beaver
        </li></ol>`
      }).as('search')

      // We have typed all but ONE character of the search string:
      cy.get('[data-cy=search]')
        .invoke('val', 'amis')
        .as('searchBox')

      // Initially, there should be no loading indicator visible
      cy.get('[data-cy=loading-indicator]')
        .should('not.be.visible')

      // Type the last character of the search string, as normal:
      cy.get('@searchBox')
        .type('k')

      // The loading indicator should be visible!
      cy.get('[data-cy=loading-indicator]')
        .should('be.visible')

      // Wait for the results to come back
      cy.wait('@search')
      cy.get('[data-cy=loading-indicator]')
        .should('not.be.visible')
    })

    // TODO: implement workaround for fetch()
    it.skip('should display an error indicator when loading fails', () => {
      cy.route({
        url: '/_search_results/amisk',
        status: 500,
        response: 'Internal Server Error!'
      }).as('search')

      // We have typed all but ONE character of the search string:
      cy.get('[data-cy=search]')
        .invoke('val', 'amis')
        .as('searchBox')

      // Initially, there should be no loading indicator visible
      cy.get('[data-cy=loading-indicator]')
        .should('not.be.visible')

      // Type the last character of the search string, as normal:
      cy.get('@searchBox')
        .type('k')

      // The loading indicator should be visible!
      cy.get('[data-cy=loading-indicator]')
        .should('be.visible')

      // Wait for the results to come back
      cy.wait('@search')
      cy.get('[data-cy=loading-indicator]')
        .should('be.visible')
        .should('have.class', 'search-progress--error')
    })
  })

})
