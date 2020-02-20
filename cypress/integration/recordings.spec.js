/**
 * Tests about hearing recording snippets.
 */
context('Recordings', function () {
  const recordingSearchPattern =
    /^https?:[/][/]localhost:8000[/]recording[/]_search[/][^/]+$/

  beforeEach(function () {
    cy.server()
  })

  describe('On the definition page', () => {
    it('should play a recording via a 🔊 icon', function () {
      // Setup the mock server
      cy.fixture('recording/_search/wâpamêw')
        .as('recordingsResults')
      cy.route(recordingSearchPattern, '@recordingsResults')
        .as('searchRecordings')

      // Get to the definition/paradigm page for "wâpamêw"
      cy.visit('/search/wâpamêw')
      cy.contains('a', 'wâpamêw')
        .click()
      cy.url()
        .should('contain', '/lemma/')

      // it SHOULD make a network request here:
      cy.wait('@searchRecordings')

      // And we should be able to click it.
      cy.get('button[data-cy=play-recording]')
        .click()

      // Note: figuring out if the audio actually played is... involved,
      // and error-prone, so it is not tested.
    })
  })
})
