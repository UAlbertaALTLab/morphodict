import { skipOn } from '@cypress/skip-test'

describe('Orthography selection', function () {
  describe('switching orthography', function () {
    it('should switch to syllabics when I click on the menu', function () {
      cy.visit('/')

      // Get the introduction: it should be in SRO
      cy.contains('h1', 'tânisi!')
        .as('greeting')

      // Switch to syllabics
      cy.get('[data-cy=language-selector]')
        .contains('SRO (êîôâ)')
        .click()
        .parent('details')
        .as('menu')
      cy.get('@menu')
        .contains('Syllabics')
        .as('option')
        .should('be.visible')
        .click()

      // Now it should be in syllabics!
      cy.get('@greeting')
        .contains('ᑖᓂᓯ!')

      // We should not see the menu
      cy.get('@option')
        .should('not.be.visible')

      // It should say so on the button
      cy.get('[data-cy=language-selector]')
        .contains('Syllabics')
        .click()

      // Opening the menu, we should find that syllabics is highligted, and
      // SRO is not:
      cy.get('@menu')
        .contains('li', 'SRO (êîôâ)')
        .should('not.have.class', 'menu-choice--selected')
      cy.get('@menu')
        .contains('li', 'Syllabics')
        .should('have.class', 'menu-choice--selected')
    })

    it('should display in syllabics given the correct cookies', function () {
      cy.setCookie('orth', 'Cans')

      // Visiting a page should be in syllabics
      cy.visit('/about')
      cy.contains('h1', 'ᐃᑘᐏᓇ')
      cy.contains('.prose__heading', 'ᓀᐦᐃᔭᐍᐏᐣ')
      cy.get('[data-cy=language-selector]')
        .contains('Syllabics')
    })

    it('should persist my preference after a page load', function () {
      // XXX: This test fails in headless mode for Electron version < v6.0
      // There was a bug with setting cookies via fetch():
      //    https://github.com/cypress-io/cypress/issues/4433
      // This should work in Cypress 3.5.0 using Chrome.
      // As of 2020-03-05 this STILL doesn't work in Travis-CI :((((
      skipOn('electron')

      cy.visit('/')

      // Get the introduction: it should be in SRO
      cy.contains('h1', 'tânisi!')
        .as('greeting')

      // Switch to syllabics
      cy.get('[data-cy=language-selector]')
        .click()
        .parent('details')
        .as('menu')
      cy.get('@menu')
        .contains('Syllabics')
        .click()

      // The cookies should have changed.
      cy.getCookie('orth')
        .should('exist')
        .its('value')
        .should('eq', 'Cans')

      // It changed on the current page:
      cy.get('@greeting')
        .contains('ᑖᓂᓯ!')

      // Now try a different page.
      cy.visit('/about')

      // It should be in syllabics.
      cy.contains('h1', 'ᐃᑘᐏᓇ')
      cy.contains('.prose__heading', 'ᓀᐦᐃᔭᐍᐏᐣ')
      cy.get('[data-cy=language-selector]')
        .contains('Syllabics')
    })
  })
})
