const { join: joinPath } = require("path");
import urls from "./urls";

// Why does this path traverse OUTSIDE of the cypress/ directory only to traverse back into it?
const CYPRESS_USER_JSON = joinPath(__dirname, "..", ".cypress-user.json");

/**
 * Fixes a bug (feature?) in Cypress for paths with non-ASCII characters. Without
 * this, `/word/wâpamêw` turns into the CP1252 `/word/w%E2pam%EAw` and then
 * `/word/w%25E2pam%25EAw`, instead of the UTF-8 `/word/w%C3%A2pam%C3%AAw/`.
 */
Cypress.Commands.overwrite("visit", (originalVisit, url, options) => {
  let newUrl = new URL(url, urls.crkeng).toString();

  if (newUrl !== url) {
    Cypress.log({
      name: "visit",
      message: `‼️  Rewriting ${url} -> ${newUrl}`,
      consoleProps: () => ({
        url,
        newUrl,
      }),
    });
  }

  return originalVisit(newUrl, options);
});

/**
 * Visit the search page for the given search query.
 */
Cypress.Commands.add(
  "visitSearch",
  { prevSubject: false },
  (searchQuery, baseUrl = urls.crkeng) => {
    Cypress.log({
      name: "visitSearch",
      message: `visiting search page for: ${searchQuery}`,
    });
    return cy.visit(`${baseUrl}/search?q=${encodeURIComponent(searchQuery)}`, {
      escapeComponents: false,
    });
  }
);

/**
 * Visit the lemma details page (mostly paradigms) for a lemma
 * The first argument has to be the exact form of the lemma (with diacritics)
 *
 * Most of the times lemmaText alone is enough. When an ambiguous case arise. This command will error out.
 * queryParams can be omitted most of the times. It's an object that can:
 *  1. select a paradigm size with "paradigmSize" key, the paradigmSize is by default BASIC
 *  2. give constraints to pin-point the lemma when lemmaText alone is
 *    ambiguous. keys can be inflectionalCategory, pos, analysis. Most of the times these can be omitted.
 *
 * pro-tip: When you need to use constraints,
 * just search for the lemma in the app and hover over the lemma link to see the constraints you need.
 */
Cypress.Commands.add(
  "visitLemma",
  { prevSubject: false },
  (lemmaText, queryParams) => {
    Cypress.log({
      name: "visitLemma",
      message: `visiting lemma detail page for: ${lemmaText}`,
    });
    queryParams = queryParams || {};
    cy.visit(
      `/word/${encodeURIComponent(lemmaText)}/?${Object.entries(queryParams)
        .map(
          ([paramName, paramValue]) =>
            paramName + "=" + encodeURIComponent(paramValue)
        )
        .join("&")}`,
      { escapeComponents: false }
    );
    // test if a redirection happens
    cy.location().should((loc) => {
      expect(
        loc.pathname,
        "lemmaText and queryParams should be enough to disambiguate the lemma"
      ).to.eq(`/word/${encodeURIComponent(lemmaText)}/`);
    });
  }
);

/**
 * Reads the .cypress-user.json file. This file should contains log-in credentials for an admin user.
 *
 * Promises an object with {username, password} properties, i.e.,
 *
 *    cy.readCypressUserCredentials()
 *      .then(({username, password}) => {
 *        // use username and password
 *      })
 *
 */
Cypress.Commands.add("readCypressUserCredentials", () => {
  return cy.readFile(CYPRESS_USER_JSON);
});

/**
 * Logs in as the user with credentials in .cypress-user.json. This user should have admin
 * privileges.
 */
Cypress.Commands.add("login", () => {
  cy.visit(Cypress.env("admin_login_url"));
  cy.get("[name=csrfmiddlewaretoken]")
    .should("exist")
    .should("have.attr", "value")
    .as("csrfToken");

  cy.readCypressUserCredentials().then(({ username, password }) => {
    cy.get("@csrfToken").then(function (token) {
      cy.request({
        method: "POST",
        url: Cypress.env("admin_login_url"),
        form: true,
        body: {
          username,
          password,
          next: Cypress.env("admin_url"),
        },
        headers: {
          "X-CSRFTOKEN": token,
        },
        followRedirect: false,
      }).then((response) => {
        expect(response.status).to.eql(302);
        expect(response.headers).to.have.property("location");
        expect(response.headers.location).to.not.contain("login");
      });
    });
  });
});

/**
 * This function returns the column header visually to the top of a td element
 * (a column header is a th element with scope=col)
 *
 * returns null if this td does not has a column header
 *
 * @param tdElement {HTMLTableDataCellElement}
 * @returns {?HTMLTableHeaderCellElement}
 */
function findColHeader(tdElement) {
  /*
  There are 3 possible cases
  1. the cell is in a pane without column headers but just a "title row"
  2. the cell has a col header
  3. the cell does not have column header nor a title row
   */

  let idx = tdElement.cellIndex;
  let upperRow = tdElement.parentElement.previousElementSibling;
  while (upperRow != null) {
    /* CASE 1: we meet a title row already, this cell does not have a column header */
    if (upperRow.cells[0].colSpan > 1) {
      return null;
    }

    const upperCell = upperRow.cells[idx];

    /* CASE 2: success */
    if (upperCell.getAttribute("scope") === "col") {
      return upperCell;
    }

    upperRow = tdElement.parentElement.previousElementSibling;
  }

  /* CASE 3 */
  return null;
}

/**
 * This function returns the title row visually to the top of a td element
 * (a title row is a th element with a long colspan attribute)
 *
 * returns null if this td does not has a title row
 *
 * @param tdElement {HTMLTableDataCellElement}
 * @returns {?HTMLTableHeaderCellElement}
 */
function findTitleRow(tdElement) {
  /* The cell may or may not have a title row */

  let upperRow = tdElement.parentElement.previousElementSibling;
  while (upperRow != null) {
    if (upperRow.cells[0].colSpan > 1) {
      return upperRow.cells[0];
    }

    upperRow = tdElement.parentElement.previousElementSibling;
  }

  return null;
}

/**
 * On a paradigm page, locate and grab the content of a cell with laser precision
 *
 * usage: cy.getParadigmCell(rowLabel, options)
 * options is an optional object with `colLabel`, or `titleLabel` or can be both
 * provide them if applicable to disambiguate
 *
 * If there are multiple matches, this command will return the first <td> matched
 *
 * e.g.
 * cy.getParadigmCell('One')
 * cy.getParadigmCell('One', {colLabel: 'Smaller/Lesser/Younger'})
 * cy.getParadigmCell('One', {titleLabel: 'Smaller/Lesser/Younger'})
 * cy.getParadigmCell('My', {titleLabel: 'One', titleLabel: 'Ownership'})
 *
 * the command will finally return a cypress-wrapped <td> element, so you can do things like
 * cy.getParadigmCell(...).contains('minôs')
 */
Cypress.Commands.add(
  "getParadigmCell",
  { prevSubject: false },
  (rowLabel, { colLabel, titleLabel }) => {
    // example code to traverse HTMLTable in different directions
    // https://jsfiddle.net/rh5aoxsL/

    // do not do cy.get('th[scope="row"]').contains(rowLabel).then(
    // because contains only yield the first element matched, but we want to to match multiples

    return cy
      .get(`th[scope="row"]:contains(${rowLabel})`)
      .then(($thCollection) => {
        for (const thElement of $thCollection) {
          // const startTH = Cypress.dom.unwrap($th)[0]

          // iterate over all tds in the row

          let colLabelMatched = false;
          let titleLabelMatched = false;

          let tdElement = thElement.nextElementSibling;
          expect(tdElement.tagName === "TD");

          while (tdElement != null) {
            if (colLabel) {
              const colHeaderTH = findColHeader(tdElement);
              if (colHeaderTH && colHeaderTH.innerText === colLabel) {
                colLabelMatched = true;
              }
            }

            if (titleLabel) {
              const titleRowTH = findTitleRow(tdElement);

              if (titleRowTH && titleRowTH.innerText === titleLabel) {
                titleLabelMatched = true;
              }
            }

            if (
              (typeof colLabel === "undefined" || colLabelMatched) &&
              (typeof titleLabel === "undefined" || titleLabelMatched)
            ) {
              return Cypress.dom.wrap(tdElement);
            }

            tdElement = tdElement.nextElementSibling;
          }
        }

        /* failed to find the cell */
      });
  }
);

/**
 * this command will type on the search bar with the given query
 * Note the search bar is not cleared, use cy.clearSearchBar to clear it
 *
 * `options` can have bool pressEnter, and integer waitTime
 *
 * pressEnter has default false, waitTime has default 500 for results to be shown.
 *
 * when pressEnter is true, an {enter} key will follow so that the search goes off immediately.
 * The site should be refreshed so no wait is needed, waitTime will default to 0
 *
 */
Cypress.Commands.add("search", { prevSubject: false }, (query, options) => {
  options = options || { pressEnter: false, waitTime: 500 };

  if (options.pressEnter === true) {
    options.waitTime = 0;
  }

  cy.get("[data-cy=search]")
    .type(query + (options.pressEnter ? "{enter}" : ""))
    .wait(options.waitTime);
});

/**
 * this command clears the search bar
 */
Cypress.Commands.add("clearSearchBar", { prevSubject: false }, () => {
  cy.get("[data-cy=search]").clear();
});

/**
 * this command clears the search bar
 */
Cypress.Commands.add(
  "searchResultsContain",
  { prevSubject: false },
  (expectedString) => {
    return cy.get("[data-cy=search-results]").should("contain", expectedString);
  }
);
