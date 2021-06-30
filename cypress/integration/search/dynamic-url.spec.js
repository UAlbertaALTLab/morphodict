context('Searching', () => {
  describe('I want to see search results by the URL', () => {
    it('performs the search by going directly to the URL', () => {
      cy.visitSearch('minos')
        .searchResultsContain('cat')
    })
  })

  describe('I want to have URL changed dynamically according to the page', function () {
    it('should display corresponding url', function () {
      cy.visit('/')
      cy.search('niya')

      cy.location('pathname')
        .should('contain', '/search')
      cy.location('search')
        .and('contain', 'q=niya')
    })

    it('should not change location upon pressing enter', function () {
      let originalPathname, originalSearch
      cy.visit('/')

      cy.search('niya')

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

    it('should add a history entry if I linger on the results for a while', function() {
      const originalQuery = 'bear'
      const originalResult = 'maskwa'

      const secondQuery = 'cat'
      const secondResult = 'minôs'

      const waitForDebounce = 500 // milliseconds
      const linger = 5000 // milliseconds

      let originalHistoryLength

      cy.visit('/')

      cy.clock({functionNames: ['setTimeout', 'clearTimeout']})

      // Issue an arbitrary query and wait for its results
      cy.get('[data-cy=search]')
        .type(originalQuery)
      cy.tick(waitForDebounce)
      cy.contains('[data-cy=search-result]', originalResult)
      cy.wrap(window.history)
        .then(history => originalHistoryLength = history.length)

      cy.tick(linger)

      // Type the second query
      cy.get('[data-cy=search]')
        .clear()
        .type(secondQuery)
      cy.tick(waitForDebounce)
      cy.contains('[data-cy=search-result]', secondResult)

      cy.wrap(window.history)
        .should(history => {
          expect(history.length).to.be.greaterThan(originalHistoryLength)
        })

      cy.go('back')
      cy.contains('[data-cy=search-result]', originalResult)
      cy.get('[data-cy=search]')
        .should('contain', originalQuery)
    })
  })
})
