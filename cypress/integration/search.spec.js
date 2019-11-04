context('Searching', () => {
  describe('I want to know what a Cree word means in English', () => {
    // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/120
    it('should search for an exact lemma', () => {
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

  describe('As an Administrator, I want to integrate words from multiple dictionary sources.', () => {
    it.only('should display the dictionary source on the page', () => {
      // acâhkos should be defined, both in the CW dictionary and the MD
      // dictionary:
      let lemma = 'acâhkos'
      cy.visit(`/search/${lemma}`)
      cy.get('[data-cy=search-results]')
        .contains('[data-cy=search-result]', lemma)
        .as('definition')

      cy.get('@definition')
        .contains('cite.cite-dict', 'CW')
        .should('be.visible')
        .should($cite => {
          expect($cite.text()).to.match(/^\s*\w+\s*$/)
        })

      cy.get('@definition')
        .contains('cite.cite-dict', 'MD')
        .should('be.visible')
        .should($cite => {
          expect($cite.text()).to.match(/^\s*\w+\s*$/)
        })
    })
  })

  // todo: the spell relax is not well integrated into the fst yet
  describe('I want the search for a Cree word to tolerate a query which may be spelled in a non-standard or slightly incorrect way.', () => {
    it('should treat apostrophes as short-Is ', () => {
      cy.visit('/')
      cy.get('[data-cy=search]')
        .type('âc\'mêw')

      cy.get('[data-cy=search-results]')
        .contains('âcimêw')
    })

    it('should forgive omitted long vowel marking', () => {
      cy.visit('/')
      cy.get('[data-cy=search]')
        .type('acimew')

      cy.get('[data-cy=search-results]')
        .contains('âcimêw')
    })
    // todo: the spell relax is not well integrated into the fst yet
    it('should handle English-influenced spelling', () => {
      cy.visit('/')
      cy.get('[data-cy=search]')
        .type('atchakosuk')

      cy.get('[data-cy=search-results]')
        .contains('acâhkos')
    })
  })

  describe('I want to TODO', () => {
    it.skip('should search the normatized form of the matched search string', () => {
      // *nipe-acimon == nipê-âcimon == PV/pe+âcimow+V+AI+Ind+Prs+1Sg
      const searchTerm = 'nipe-acimon'
      cy.visit('/')
      cy.get('[data-cy=search]')
        .type(searchTerm)

      cy.get('[data-cy=search-results]')
        .contains('[data-cy=search-result]', /Form of/i)
        .as('searchResult')

      // normatized form:
      cy.get('@searchResult')
        .contains('[data-cy=definition-title]', 'nipê-âcimon')
    })
  })

  describe('Loading indicator', () => {
    beforeEach(() => {
      cy.server()
      cy.visit('/')
    })

    it('should display a loading indicator', () => {
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

    it('should display an error indicator when loading fails', () => {
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
