context('Searching', () => {

  describe('A tooltip should show up when the user click/hover on the question mark beside the matched wordform', () => {
    // fixme: somehow click does not work and cypress does not support hovering
    //    also tried manually triggering "mouseon"/"mouseover" events but no luck
    it.skip('should show tooltip when I click on the question mark beside ê-wâpamat', () => {
      cy.visit('/')
      cy.get('[data-cy=search]')
        .type('ewapamat')

      cy.wait(500)

      // not visible in the beginning
      cy.get('[data-cy=linguistic-breakdown]').should('not.be.visible')

    })}

  )


  describe('I want to know what a Cree word means in English', () => {
    // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/120
    it('should search for an exact lemma', () => {
      cy.visit('/')
      cy.get('[data-cy=search]')
        .type('minos')

      cy.get('[data-cy=search-results]')
        .should('contain', 'cat')
    })

    it('should perform the search by going directly to the URL', () => {
      cy.visit('/search/minos')

      cy.get('[data-cy=search-results]')
        .should('contain', 'cat')
    })
  })

  describe('search results should be ranked by modified levenshtein distance', () => {
    it('should show nipa before nipaw if the search string is nipa', () => {
      // on the previous implementation nipaw is showed first
      cy.visit('/search/nipa')

      cy.get('[data-cy=search-results]').first()
        .should('contain', 'nipa')
        .and('contain', 'Means, during the night')
    })
  })

  describe('As an Administrator, I want to integrate words from multiple dictionary sources.', () => {
    it('should display the dictionary source on the page', () => {
      // atâhk should be defined, both in the CW dictionary and the MD
      // dictionary:
      let lemma = 'atâhk'
      let dicts = ['CW', 'MD']

      cy.visit(`/search/${lemma}`)
      cy.get('[data-cy=search-results]')
        .contains('[data-cy=search-result]', lemma)
        .as('definition')

      // Check each citation.
      for (let id of dicts) {
        cy.get('@definition')
          .contains('cite.cite-dict', id)
          .should('be.visible')
          .should($cite => {
            expect($cite.text()).to.match(/^\s*\w+\s*$/)
          })
      }
    })
  })

  describe('I want the search for a Cree word to tolerate a query which may be spelled in a non-standard or slightly incorrect way.', () => {
    it('should treat apostrophes as short-Is ', () => {
      cy.visit('/')
      cy.get('[data-cy=search]')
        .type('tan\'si')

      cy.get('[data-cy=search-results]')
        .contains('tânisi')
    })

    it('should forgive omitted long vowel marking', () => {
      cy.visit('/')
      cy.get('[data-cy=search]')
        .type('acimew')

      cy.get('[data-cy=search-results]')
        .contains('âcimêw')

      cy.get('[data-cy=search]')
        .clear()
        .type('ayiman')

      cy.get('[data-cy=search-results]')
        .contains('âyiman')

    })

    it('should handle English-influenced spelling', () => {
      cy.visit('/')
      cy.get('[data-cy=search]')
        .type('atchakosuk')

      cy.get('[data-cy=search-results]')
        .contains('atâhk')
    })
  })

  describe('I want to see the normatize form of my search', () => {
    it('should search the normatized form of the matched search string', () => {
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

      cy.get('@searchResult').get('[data-cy=reference-to-lemma]')
        .contains( 'âcimow')
    })
  })

  it('should leave out not normatized content', () => {
    // nipa means "Kill Him" in MD
    cy.visit('/search/nipa')

    cy.get('[data-cy=search-results]')
      .should('contain', 'sleeps')
      .and('not.contain', 'Kill')
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
