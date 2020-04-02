/**
 * Tests about hearing recording snippets.
 */
context('Recordings', function () {
  describe('On the definition page', () => {
    it('should play a recording via a 🔊 icon', function () {
      cy.fixture('recording/_search/wâpamêw', 'utf-8')
        .as('recordingsResults')

      // Get to the definition/paradigm page for "wâpamêw"
      cy.visitSearch('wâpamêw')
      cy.contains('a', 'wâpamêw')
        .click()
      cy.url()
        .should('contain', '/word/')

      // TODO: we should stub a network request,
      // but Cypress can't deal with fetch() requests :/
      // It has to use a polyfill, but for various reasons,
      // that's annoying and brittle
      //  (e.g., if the URL changes, the polyfill needs
      //   to be re-enabled).

      // And we should be able to click it.
      cy.get('button[data-cy=play-recording]')
        .click()

      // Note: figuring out if the audio actually played is... involved,
      // and error-prone, so it is not tested.
      // If you *want* to mock the Audio constructor... I mean, you can...
      // https://github.com/cypress-io/cypress/issues/1750#issuecomment-390751415
    })

    it('should display the lemma\'s multiple speakers on hover/click', () => {
      // begin from the start page 
      cy.visit('/');

      // select the searchbar
      cy.get('[data-cy=search]')

      // look up a word (wapamew)
      .type('wapamew');

      // select the word,
      cy.get('[data-cy=definition-title').first().click();

      // then hover/focus on the speaker icon

      // the tooltip of the lemma's speakers should pop up
    })
  })
})
