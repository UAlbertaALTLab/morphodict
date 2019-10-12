/**
 * General tests about the website's behaviour as a regular website.
 */
context('General', () => {
  beforeEach(() => {
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

  describe('Changing the language', () => {
    it('should be accessible from a menu', () => {
      cy.get('[data-cy=language-selector]')
        .type('{enter}')

      cy.get('[data-cy=language-choices]')
        .should('be.visible')
        .contains('nêhiyawêwin')
        .click()

      // TODO: assert we're in Cree!
    })
  })

  describe('I want see all written Cree in Western Cree Syllabics', () => {
    it('should be accessible from the language selector', () => {
      cy.get('[data-cy=language-selector]')
        .type('{enter}')

      cy.get('[data-cy=orthography-choices]')
        .should('be.visible')
        .contains('ᒐᐦᑭᐯᐦᐃᑲᓇ')
        .click()

      cy.get('h1')
        .contains('ᐃᑘᐏᓇ')
    })
  })
})
