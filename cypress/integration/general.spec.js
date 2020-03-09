/**
 * General tests about the website's behaviour as a regular website.
 */
context('General', function () {
  beforeEach(function () {
    cy.visit('/')
  })

  describe('Visiting the home page', () => {
    it('should say “itwêwina” in the header', () => {
      cy.get('h1')
        .should('be.visible')
        .should('contain', 'itwêwina')
    })

    it('should greet the users in the content', () => {
      cy.get('main')
        .contains('h1, h2', /\bt[âā]n[i']?si\b/)
        .should('be.visible')
    })
  })

  describe('Changing the language', function () {
    it('should be accessible from a menu', function () {
      this.skip('language selector not implemented')

      cy.get('[data-cy=language-selector]')
        .type('{enter}')

      cy.get('[data-cy=language-choices]')
        .should('be.visible')
        .contains('nêhiyawêwin')
        .click()

      // TODO: assert we're in Cree!
    })
  })

  describe('I want see all written Cree in Western Cree Syllabics', function () {
    it('should be accessible from the language selector', function () {
      cy.get('[data-cy=language-selector]')
        .type('{enter}')

      cy.get('[data-cy=orthography-choices]')
        .should('be.visible')
        .contains('Syllabics')
        .click()

      cy.get('h1')
        .contains('ᐃᑘᐏᓇ')
    })
  })

  describe('I want to search for complex Cree words', function () {
    // See: https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/150
    it('should have a clickable example on the front page', function () {
      const word = 'ê-kî-nitawi-kâh-kîmôci-kotiskâwêyâhk'

      cy.visit('/')

      cy.get('[data-cy=long-word-example]')
        .should('contain', word)
        .click()

      // we should be on a new page.
      cy.url()
        .should('contain', '/search')

      cy.get('[data-cy=search-results]')
        .should('contain', word)
    })
  })
})
