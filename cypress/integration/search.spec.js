context('Searching', () => {
  describe('I want to know what a Cree word means in English', () => {
    // https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/120
    it('should search for an exact lemma', () => {
      cy.visitSearch('minos')
        .searchResultsContain('cat')
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

      cy.visitSearch('tan\'si')
        .searchResultsContain('tânisi')
    })

    it('should forgive omitted long vowel marking', () => {
      cy.visit('/')

      cy.visitSearch('acimew')
        .searchResultsContain('âcimêw')

      cy.clearSearchBar()

      cy.visitSearch('ayiman')
        .searchResultsContain('âyiman')

    })

    it('should handle English-influenced spelling', () => {
      cy.visitSearch('atchakosuk')
        .searchResultsContain('atâhk')
    })
  })

  describe('I want to see the normatize form of my search', () => {
    it('should search the normatized form of the matched search string', () => {
      // *nipe-acimon == nipê-âcimon == PV/pe+âcimow+V+AI+Ind+1Sg
      const searchTerm = 'nipe-acimon'
      cy.visit('/')

      cy.visitSearch(searchTerm)

      cy.get('[data-cy=search-results]')
        .contains('[data-cy=search-result]', /Form of/i)
        .as('searchResult')

      // normatized form:
      cy.get('@searchResult')
        .contains('[data-cy=definition-title]', 'nipê-âcimon')

      cy.get('@searchResult').get('[data-cy=reference-to-lemma]')
        .contains('âcimow')
    })
  })

  it('should leave out not normatized content', () => {
    // nipa means "Kill Him" in MD
    cy.visitSearch('nipa')
      .searchResultsContain('sleeps')
      .and('not.contain', 'Kill')
  })


  describe("When I perform a search, I should see the 'info' icon on corresponding entries", () => {
    // Right – this is the test for issue #239 (https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/239).

    // At present, I want to target the definition's title, then look at the children to see if the the 'i' icon is
    // there. There's probably a more elegant way to do this but I think that'll come as I become more comfortable with the codebase.
    it("should show the 'info' icon to allow users to access additional information", () => {
      // borrowed the following four lines from above and used 'nipaw' for testing purposes.
      const searchTerm = 'niya'
      cy.visitSearch(searchTerm)

      cy.get('[data-cy=search-result]').find('[data-cy=information-mark]')
    })
  })

  describe('A tooltip should show up when the user click/focus on the i icon beside the matched wordform', () => {
    it('should show tooltip when the user focuses on the i icon beside ê-wâpamat', () => {
      cy.visitSearch('ewapamat')

      // not visible at the start
      cy.get('[data-cy=linguistic-breakdown]').should('not.be.visible')
        .and('contain', 'Action word') // verb

      cy.get('[data-cy=information-mark]').first().focus()

      cy.get('[data-cy=linguistic-breakdown]').should('be.visible')
    })

    it('should show tooltip with relevant linguistic breakdowns when the user clicks on the i icon beside ê-wâpamat', () => {
      cy.visitSearch('ewapamat')

      // not visible at the start
      cy.get('[data-cy=linguistic-breakdown]').should('not.be.visible')

      // has to use force: true since div is not clickable
      cy.get('[data-cy=information-mark]').first().click()

      cy.get('[data-cy=linguistic-breakdown]').should('be.visible')
        .and('contain', 'wâpam-') // stem
        // NOTE: this depends on Antti's relabellings; if they change,
        // this assertion has to change :/
        .and('contain', 'Action word - like') // VTA
        .and('contain', 'you (one) → him/her')  // 3Sg -> 4Sg/PlO
    })

    it('should show linguistic breakdowns as an ordered list when the user clicks on the i icon beside a word', () => {

      cy.visitSearch('nipaw')

      // tab through the elements to force the tooltip to pop up
      cy.get('[data-cy=information-mark]').first().click()

      // see the linguistic breakdown as an ordered list
      cy.get('[data-cy=linguistic-breakdown]').contains('li', 'Action word')
    })

    it('should allow the tooltip to be focused on when the user tabs through it', () => {
      // goodness, that's a mouthful and should _probably_ be worded better.
      // begin from the homepage
      cy.visit('/')
      cy.search('nipaw')

      // tab through the page elements until arriving on the '?' icon
      cy.get('[data-cy=information-mark]').first().click()

      // it should trigger the focus icon's outline's focused state
      cy.get('[data-cy=information-mark]').first().focus().should('have.css', 'outline')
    })

    it('should not overlap other page elements when being displayed in the page', () => {
      // Eddie's comment used a very long word in `e-ki-nitawi-kah-kimoci-kotiskaweyahk`, so we will use that!
      cy.visitSearch('e-ki-nitawi-kah-kimoci-kotiskaweyahk')


      // force the tooltip to appear
      cy.get('[data-cy=information-mark]').first().click({force: true})

      // check that the z-index of the tooltip is greater than that of all other page elements
      cy.get('[data-cy=information-mark]').first().focus().next().should('have.css', 'z-index', '1') // not a fan of this because of how verbose it is – if there's amore concise way of selecting for a non-focusable element, I'm all ears!
    })

    /**
     * https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/549
     */
    it('displays the stem prominently in the linguistic breakdown', function () {
      cy.visitSearch('pê-nîmiw')

      // Open the linguistic breakdown popup
      cy.get('[data-cy=search-result]')
        .find('[data-cy=information-mark]')
        .first()
        .click()

      cy.get('[data-cy=linguistic-breakdown]')
        .as('linguistic-breakdown')
        .should('be.visible')

      cy.get('@linguistic-breakdown')
        .contains('nîmi-')
        .should(($el) => {
          expect(+$el.css('font-weight')).to.be.greaterThan(400)
        })
    })

    it('displays the suffix features in the linguistic breakdown', function () {
      cy.visitSearch('pê-nîmiw')

      // Open the linguistic breakdown popup
      cy.get('[data-cy=search-result]')
        .find('[data-cy=information-mark]')
        .first()
        .click()

      cy.get('[data-cy=linguistic-breakdown]')
        .as('linguistic-breakdown')
        .should('be.visible')
      cy.get('@linguistic-breakdown')
        .contains('li', 'Action word')
      cy.get('@linguistic-breakdown')
        .contains('li', 'ni-/ki- word')
      cy.get('@linguistic-breakdown')
        .contains('li', 's/he')
    })
  })

  describe('When results are not found', function () {
    // TODO: we should probably choose a more mature example ¯\_(ツ)_/¯
    const NON_WORD = 'pîpîpôpô'

    it('should report no results found for ordinary search', function () {
      cy.visitSearch(NON_WORD)

      cy.location().should((loc) => {
        expect(loc.pathname).to.eq('/search')
        expect(loc.search).to.contain(`q=${encodeURIComponent(NON_WORD)}`)
      })

      // There should be something telling us that there are no results
      cy.get('[data-cy=no-search-result]')
        .and('contain', 'No results found')
        .should('contain', NON_WORD)
    })

    it('should report no results found when visiting the page directly', function () {
      cy.visitSearch(NON_WORD)

      cy.get('[data-cy=no-search-result]')
        .and('contain', 'No results found')
        .should('contain', NON_WORD)
    })
  })

  // See: https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/445#:~:text=4.%20Inflected%20form
  describe('display of the header', function () {
    const lemma = 'nîmiw'
    const wordclassEmoji = '➡️' // the arrow is the most consistent thing, which means verb
    const inflectionalCategory = /VAI-v|VAI-1/
    const plainEnglishInflectionalCategory = 'like: nipâw'
    const nonLemmaFormWithDefinition = 'nîminâniwan'
    const nonLemmaFormWithoutDefinition = 'ninîmin'
    const nonLemmaDefinition = 'it is a dance'

    it('should display the match wordform and word class on the same line for lemmas', function () {
      cy.visitSearch(fudgeUpOrthography(lemma))

      // make sure we get at least one search result...
      cy.get('[data-cy=search-result]')
        .as('search-result')

      // now let's make sure the NORMATIZED form is in the search result
      cy.get('@search-result')
        .contains('header [data-cy="matched-wordform"]', lemma)
      cy.get('@search-result')
        .contains('header [data-cy="word-class"]', wordclassEmoji)
      cy.get('@search-result')
        .contains('header [data-cy="word-class"]', plainEnglishInflectionalCategory)
    })

    it('should display the matched word form and its lemma/word class on separate lines for non-lemmas', function () {
      cy.visitSearch(fudgeUpOrthography(nonLemmaFormWithoutDefinition))

      // make sure we get at least one search result...
      cy.get('[data-cy=search-result]')
        .as('search-result')

      // now let's make sure the NORMATIZED form is in the search result
      cy.get('@search-result')
        .contains('header [data-cy="matched-wordform"]', nonLemmaFormWithoutDefinition)

      // now make sure the 'form of' text is below that
      cy.get('@search-result')
        .get('header [data-cy="elaboration"]')
        .as('elaboration')

      cy.get('@elaboration')
        .get('[data-cy="reference-to-lemma"]')
        // TODO: should we be testing for this exact text?
        .should('contain', 'form of')
        .and('contain', lemma)
      cy.get('@elaboration')
        .contains('[data-cy="word-class"]', wordclassEmoji)
      cy.get('@elaboration')
        .contains('[data-cy="word-class"]', plainEnglishInflectionalCategory)
    })

    // See: https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/445#:~:text=4.%20Inflected%20form
    it('should display an inflected form with a definition AND its lemma', function () {
      cy.visitSearch(fudgeUpOrthography(nonLemmaFormWithDefinition))

      // make sure we get at least one search result...
      cy.get('[data-cy=search-result]')
        .as('search-result')

      // make sure the NORMATIZED form is in the search result
      cy.get('@search-result')
        .contains('header [data-cy="matched-wordform"]', nonLemmaFormWithDefinition)

      // Open the linguistic breakdown popup
      cy.get('@search-result')
        .find('[data-cy=information-mark]')
        .as('information-mark')
        .first()
        .click()

      // See the linguistic breakdown as an ordered list
      cy.get('[data-cy=linguistic-breakdown]')
        .first()
        .should('be.visible')
        .contains('li', 'ni-/ki- word')

      // Close the tooltip
      cy.get('@information-mark')
        .first()
        .blur()

      // make sure it has a definition
      cy.get('@search-result')
        // TODO: change name of [data-cy="lemma-meaning"] as it's misleading :/
        .contains('[data-cy="lemma-meaning"]', nonLemmaDefinition)

      // "form of nîmiw"
      cy.get('@search-result')
        .get('[data-cy="reference-to-lemma"]')
        .should('contain', 'form of')
        .and('contain', lemma)

      cy.get('@search-result')
        .get('[data-cy="elaboration"]')
        .as('elaboration')

      cy.get('@elaboration')
        .get('[data-cy="word-class"]')
        .should('contain', wordclassEmoji)
        .and('contain', plainEnglishInflectionalCategory)

      // Inflectional category tool tip
      cy.get('@elaboration')
        .get('[data-cy="word-class"]')
        .first()
        .click()
      cy.get('@elaboration')
        .get('[role="tooltip"]')
        .should('be.visible')
      cy.get('@elaboration')
        .contains('[role="tooltip"]', inflectionalCategory)
    })

    // See: https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/445#:~:text=5.%20Inflected%20form%20without%20definition
    it('should display an inflected form and its lemma', function () {
      cy.visitSearch(fudgeUpOrthography(nonLemmaFormWithoutDefinition))

      // make sure we get at least one search result...
      cy.get('[data-cy=search-result]')
        .as('search-result')

      // make sure the NORMATIZED form is in the search result
      cy.get('@search-result')
        .contains('header [data-cy="matched-wordform"]', nonLemmaFormWithoutDefinition)

      // Open the linguistic breakdown popup
      cy.get('@search-result')
        .get('[data-cy=information-mark]')
        .first()
        .as('information-mark')
        .click()

      // See the linguistic breakdown as an ordered list
      cy.get('[data-cy=linguistic-breakdown]')
        .first()
        .should('be.visible')
        .contains('li', 'ni-/ki- word')

      // Close the tooltip
      cy.get('@information-mark')
        .blur()

      // "form of nîmiw"
      cy.get('@search-result')
        .get('[data-cy="reference-to-lemma"]')
        .should('contain', 'form of')
        .and('contain', lemma)

      cy.get('@search-result')
        .get('[data-cy="elaboration"]')
        .as('elaboration')

      cy.get('@elaboration')
        .get('[data-cy="word-class"]')
        .should('contain', wordclassEmoji)
        .and('contain', plainEnglishInflectionalCategory)

      // Inflectional category tool tip
      cy.get('@elaboration')
        .get('[data-cy="word-class"]')
        .first()
        .click()
      cy.get('@elaboration')
        .get('[role="tooltip"]')
        .should('be.visible')
      cy.get('@elaboration')
        .contains('[role="tooltip"]', inflectionalCategory)
    })

    // See: https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/445#:~:text=6.%20Lemma%20definition
    it('should display an inflected form and its lemma', function () {
      cy.visitSearch(fudgeUpOrthography(lemma))

      // make sure we get at least one search result...
      cy.get('[data-cy=search-result]')
        .as('search-result')

      // make sure the NORMATIZED form is in the search result
      cy.get('@search-result')
        .contains('header [data-cy="matched-wordform"]', lemma)

      // Open the linguistic breakdown popup
      cy.get('@search-result')
        .get('[data-cy=information-mark]')
        .first()
        .as('information-mark')
        .click()

      // See the linguistic breakdown as an ordered list
      cy.get('[data-cy=linguistic-breakdown]')
        .first()
        .should('be.visible')
        .contains('li', 'ni-/ki- word')

      // Close the tooltip
      cy.get('@information-mark')
        .blur()

      cy.get('@search-result')
        .get('[data-cy="elaboration"]')
        .as('elaboration')

      cy.get('@elaboration')
        .get('[data-cy="word-class"]')
        .should('contain', wordclassEmoji)
        .and('contain', plainEnglishInflectionalCategory)

      // Inflectional category tool tip
      cy.get('@elaboration')
        .get('[data-cy="word-class"]')
        .first()
        .click()
      cy.get('@elaboration')
        .get('[role="tooltip"]')
        .should('be.visible')
      cy.get('@elaboration')
        .contains('[role="tooltip"]', inflectionalCategory)
    })

    // Regression: it used to display 'Preverb — None' :/
    it.skip('should not display wordclass help if it does not exist', function () {
      // Preverbs do not have an elaboration (right now)
      const preverb = 'nitawi-'
      cy.visitSearch(preverb)

      // TODO: I DON'T KNOW WHAT IT SHOULD ACTUALL SHOW 😱
      cy.get('[data-cy=search-result]')
        .contains('[data-cy=word-class]', 'Preverb')
        .should('not.contain', 'None')
    })

    // Regression: it used to display 'like — pê-' :/
    it('should not display wordclass emoji if it does not exist', function () {
      // Preverbs do not have an elaboration (right now)
      const preverb = 'nitawi-'
      cy.visitSearch(preverb)

      cy.get('[data-cy=search-result]')
        .first()
        .find('[data-cy=word-class]')
        .should('contain', 'like: pê-')
        .and('not.contain', 'None')
    })

    /**
     * @returns {string} the wordform, as if you typed very quickly on your niece's peanut butter-smeared iPad
     */
    function fudgeUpOrthography(normatizedWordform) {
      return normatizedWordform.normalize('NFKD').replace(/[\u0300-\u035f-]/g, '').toLowerCase()
    }
  })
})
