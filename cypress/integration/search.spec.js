context('Searching', () => {
  describe('A tooltip should show up when the user click/focus on the i icon beside the matched wordform', () => {
    it('should show tooltip when the user focuses on the i icon beside ê-wâpamat', () => {
      cy.visit('/')
      cy.get('[data-cy=search]')
        .type('ewapamat')

      // not visible at the start
      cy.get('[data-cy=linguistic-breakdown]').should('not.be.visible')
        .and('contain', 'wâpamêw') // lemma
        .and('contain', 'Action word') // verb

      cy.get('[data-cy=information-mark]').first().focus()

      cy.get('[data-cy=linguistic-breakdown]').should('be.visible')
    })

    it('should show tooltip when the user clicks on the i icon beside ê-wâpamat', () => {
      cy.visit('/')
      cy.get('[data-cy=search]')
        .type('ewapamat')

      // not visible at the start
      cy.get('[data-cy=linguistic-breakdown]').should('not.be.visible')

      // has to use force: true since div is not clickable
      cy.get('[data-cy=information-mark]').first().click({force:true})

      cy.get('[data-cy=linguistic-breakdown]').should('be.visible')
        .and('contain', 'wâpamêw') // lemma
        .and('contain', 'Action word') // verb
    })

    it('should show the tooltip\'s linguistic breakdowns on separate lines as list items', () => {
      cy.visit('/');
      cy.get('[data-cy=search]').type('achakos');

      // I think I have to stub this test with part of the code from the test above 🤔
      
    })
  })

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
      cy.visit('/search?q=minos', { escapeComponents: false })

      cy.get('[data-cy=search-results]')
        .should('contain', 'cat')
    })
  })

  describe('search results should be ranked by modified levenshtein distance', () => {
    it('should show nipîhk before nîpîhk if the search string is the former', () => {
      cy.visitSearch('nipîhk')

      cy.get('[data-cy=search-results]').first()
        .should('contain', 'nipîhk')
        .and('contain', 'water')
    })
  })

  describe('As an Administrator, I want to integrate words from multiple dictionary sources.', () => {
    it('should display the dictionary source on the page', () => {
      // atâhk should be defined, both in the CW dictionary and the MD
      // dictionary:
      let lemma = 'atâhk'
      let dicts = ['CW', 'MD']

      cy.visitSearch(lemma)
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
    cy.visitSearch('nipa')

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


  describe('When I perform a search, I should see the \'info\' icon on corresponding entries', () => {
    // Right – this is the test for issue #239 (https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/239).

    // At present, I want to target the definition's title, then look at the children to see if the the 'i' icon is
    // there. There's probably a more elegant way to do this but I think that'll come as I become more comfortable with the codebase.
    it('should show the \'info\' icon to allow users to access additional information', () => {
      // borrowed the following four lines from above and used 'nipaw' for testing purposes.
      const searchTerm = 'niya'
      cy.visit('/')
      cy.get('[data-cy=search]')
        .type(searchTerm)

      cy.get('[data-cy=search-result]').find('[data-cy=information-mark]')
    })
  })

  describe('When I type at the search bar, I should see results instantly', function () {
    it('should display results in the page', function () {
      cy.visit('/')

      cy.get('[data-cy=search]')
        .type('niya')

      cy.location('pathname')
        .should('contain', '/search')
      cy.location('search')
        .and('contain', 'q=niya')
    })

    it('should not change location upon pressing enter', function () {
      let originalPathname, originalSearch
      cy.visit('/')

      cy.get('[data-cy=search]')
        .type('niya')

      cy.location().should((loc) => {
        originalPathname = loc.pathname
        originalSearch = loc.search
        expect(loc.pathname).to.eq('/search')
        expect(loc.search).to.contain('q=niya')
      })

      // Press ENTER!
      cy.get('[data-cy=search]')
        .type('{Enter}')

      cy.location().should(loc => {
        expect(loc.pathname).to.eq(originalPathname)
        expect(loc.search).to.eq(originalSearch)
      })
    })
  })
})
