context('Assertions', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  describe('Example assertion', () => {
    it('the page should say itwêwina', () => {
      // https://on.cypress.io/should
      cy.get('h1')
        .should('contain', 'itwêwina');
    });
  });
});
