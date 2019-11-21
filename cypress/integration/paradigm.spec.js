context('Paradigms', () => {
  describe(' I want to search for a Cree word and see its inflectional paradigm', () => {
    it('should display the paradigm for an NA word', () => {
      cy.visit('/search/acâhkos');
      cy.get('[data-cy=search-results]')
        .contains('a', 'acâhkos')
        .click();

      cy.get('[data-cy=paradigm]')
        .as('paradigm');

      cy.get('@paradigm')
        .should('contain', 'acâhkos')
        .and('contain', 'acâhkosak')
        .and('contain', 'acâhkosa');

      cy.get('@paradigm')
        .contains('th[scope=row]', 'Further')

      // TODO: the next test should be here, but it is broken because the
      // upstream layouts are broken :/ 

      // TODO: acâhkos is already diminutive, so it should not display the
      // diminutive paradigm.
    });

    it.skip('should display titles within the paradigm', () => {
      // TODO: move this test into the previous test when the layout is fixed.
      cy.visit('/search/acâhkos');
      cy.get('[data-cy=search-results]')
        .contains('a', 'acâhkos')
        .click();

      cy.get('[data-cy=paradigm]')
        .as('paradigm');

      cy.get('@paradigm')
        .contains('.paradigm-title', 'Ownership')

      // TODO: acâhkos is already diminutive, so it should not display the
      // diminutive paradigm.
    })
  })
});
