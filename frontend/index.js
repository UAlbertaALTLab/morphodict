// "Urls" is a magic variable that allows use to reverse urls in javascript
// See https://github.com/ierror/django-js-reverse

// Process CSS with PostCSS automatically. See rollup.config.js for more
// details.
import "./css/styles.css";
import { createTooltip } from "./js/tooltip";
import {
  fetchFirstRecordingURL,
  fetchRecordingURLForEachWordform,
  retrieveListOfSpeakers,
} from "./js/recordings.js";
import { fetchCorpusURL } from "./js/corpus.js";
import * as orthography from "./js/orthography.js";
import {
  emptyElement,
  removeElement,
  showElement,
  hideElement,
} from "./js/dom-utils.js";
import {
  indicateLoading,
  indicateLoadedSuccessfully,
  indicateLoadingFailure,
  hideLoadingIndicator,
} from "./js/loading-bar.js";
import { debounce } from "./js/debounce.js";
import { setupParadigm } from "./js/paradigm.js";
import * as settings from "./js/settings-page.js";
import * as toast from "./js/toast.js";
import { loadParadigmAudio } from "./js/paradigm-recording";

import "bootstrap/js/dist/collapse.js";
import "./css/bootstrap.scss";
//import '../node_modules/bootstrap/dist/css/bootstrap.css'
///////////////////////////////// Constants //////////////////////////////////

const NO_BREAK_SPACE = "\u00A0";

/**
 * Milliseconds, we only send search requests after this long of time of inactivity has passed.
 * Prevents too many invalid requests from being sent during typing
 *
 * Check the brief blog post to read a study about people's typing speed:
 * https://madoshakalaka.github.io/2020/08/31/how-hard-should-you-debounce-on-a-responsive-search-bar.html
 * @type {number}
 */
const SEARCH_BAR_DEBOUNCE_TIME = 450;

//////////////////////////////// On page load ////////////////////////////////

document.addEventListener("DOMContentLoaded", () => {
  let csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
  orthography.registerEventListener(csrfToken);

  setupSearchBar();
  settings.setupAutoSubmitForEntirePage();
  toast.setGlobalElement(document.getElementById("toast"));

  let route = makeRouteRelativeToSlash(window.location.pathname);
  // Tiny router.
  if (route === "/") {
    // Homepage
    setSubtitle(null);
  } else if (route === "/about") {
    // About page
    setSubtitle("About");
  } else if (route === "/contact-us") {
    // Contact page
    setSubtitle("Contact us");
  } else if (route === "/search") {
    // Search page
    prepareSearchResults(getSearchResultList());
    setupRefocus();
  } else if (route.match(/^[/]word[/].+/)) {
    // Word detail/paradigm page. This one has the 🔊 button.
    setSubtitle(getEntryHead());
    setupAudioOnPageLoad();
    setupCorpusOnPageLoad();
    setupParadigm();
    prepareTooltips();
    loadParadigmAudio();
  }
});

function setupSearchBar() {
  const searchBar = document.getElementById("search");
  const debouncedLoadSearchResults = debounce(() => {
    loadSearchResults(searchBar);
  }, SEARCH_BAR_DEBOUNCE_TIME);

  searchBar.addEventListener("input", () => {
    indicateLoading();
    debouncedLoadSearchResults();
  });
}

/**
 * clean paradigm details
 */
function cleanDetails() {
  removeElement(document.getElementById("definition"));
}

function showProse() {
  showElement(document.getElementById("prose"));
}

function hideProse() {
  hideElement(document.getElementById("prose"));
}

/**
 * Prepares interactive elements of each search result, including:
 *  - tooltips
 *  - recordings
 *
 * @param {Element} searchResultsList
 */
function prepareSearchResults(searchResultsList) {
  prepareTooltips();
  loadRecordingsForAllSearchResults(searchResultsList);
  loadCorpusForAllSearchResults(searchResultsList);
}

/**
 * Given a list of search results, this will attempt to match a recording to
 * its match wordform.
 *
 * @param {Element} searchResultsList
 */
async function loadRecordingsForAllSearchResults(searchResultsList) {
  let elementWithWordform = [];
  let requestedWordforms = new Set();

  for (let element of searchResultsList.querySelectorAll("[data-wordform]")) {
    let wordform = element.dataset.wordform;
    elementWithWordform.push([element, wordform]);
    requestedWordforms.add(wordform);
  }

  let wordform2recordingURL;
  try {
    wordform2recordingURL = await fetchRecordingURLForEachWordform(
      requestedWordforms
    );
  } catch {
    // fail silently ¯\_(ツ)_/¯
    return;
  }

  for (let [element, wordform] of elementWithWordform) {
    let recordingURL = wordform2recordingURL.get(wordform);
    if (recordingURL) {
      createAudioButton(recordingURL, element);
    }
  }
}

/**
 * Given a list of search results, this will attempt to match a recording to
 * its match wordform.
 *
 * @param {Element} searchResultsList
 */
async function loadCorpusForAllSearchResults(searchResultsList) {
  let elementWithWordform = [];
  let requestedWordforms = new Set();

  for (let element of searchResultsList.querySelectorAll("[data-wordform]")) {
    let wordform = element.dataset.wordform;
    elementWithWordform.push([element, wordform]);
    requestedWordforms.add(wordform);
  }

  for (let [element, wordform] of elementWithWordform) {
    let corpusURL = await fetchCorpusURL(
      wordform,
      element.hasAttribute("data-main-lemma")
    );
    if (corpusURL) {
      createCorpusButton(corpusURL, element);
    }
  }
}

/**
 * Attach relevant handlers to **ALL** tooltip icons on the page.
 */
function prepareTooltips() {
  let tooltips = document.querySelectorAll("[data-has-tooltip]");

  for (let icon of tooltips) {
    let tooltip = icon.nextElementSibling;
    if (!tooltip.classList.contains("tooltip")) {
      throw new Error("Expected tooltip to be direct sibling of icon");
    }
    createTooltip(icon, tooltip);
  }
}

/**
 * use AJAX to load search results in place
 *
 * @param {HTMLInputElement} searchInput
 */
function loadSearchResults(searchInput) {
  let userQuery = searchInput.value;
  let searchResultList = getSearchResultList();

  if (userQuery !== "") {
    changeTitleBySearchQuery(userQuery);
    issueSearch();
  } else {
    goToHomePage();
  }

  function issueSearch() {
    let searchURL = Urls["dictionary-search-results"](userQuery);

    window.history.replaceState(null, "", urlForQuery(userQuery));
    hideProse();

    fetch(searchURL)
      .then((response) => {
        if (response.ok) {
          return response.text();
        }
        return Promise.reject();
      })
      .then((html) => {
        // user input may have changed during the request
        const inputNow = searchInput.value;

        if (inputNow !== userQuery) {
          // input has changed, so ignore this request to prevent flashing
          // out-of-date search results
          return;
        }

        // Remove loading cards
        indicateLoadedSuccessfully();
        cleanDetails();
        searchResultList.innerHTML = html;
        prepareSearchResults(searchResultList);
      })
      .catch(() => {
        indicateLoadingFailure();
      });
  }

  function goToHomePage() {
    window.history.replaceState(null, "", Urls["dictionary-index"]());

    showProse();

    hideLoadingIndicator();
    emptyElement(searchResultList);
  }

  /**
   * Returns a URL that search for the given query.
   *
   * The URL is constructed by using the <form>'s action="" attribute.
   */
  function urlForQuery(userQuery) {
    let form = searchInput.closest("form");
    return form.action + `?q=${encodeURIComponent(userQuery)}`;
  }
}

/**
 * Change tab title according to user input in the search bar
 *
 * @param inputVal {string}
 */
function changeTitleBySearchQuery(inputVal) {
  setSubtitle(inputVal ? "🔎 " + inputVal : null);
}

let defaultTitle = document.title;

function setSubtitle(subtitle) {
  document.title = subtitle ? `${subtitle} — ${defaultTitle}` : defaultTitle;
}

/**
 * Sets up the (rudimentary) audio link on page load.
 */
function setupAudioOnPageLoad() {
  let title = document.getElementById("head");
  if (!title) {
    // Could not find a head on the page.
    return;
  }

  // TODO: setup baseURL from <link rel=""> or something.
  let wordform = getEntryHead();

  fetchFirstRecordingURL(wordform)
    .then((recordingURL) => {
      if (recordingURL === undefined) {
        // The API could not find a recording for this wordform ¯\_(ツ)_/¯
        return;
      }

      // TODO: it shouldn't be placed be **inside** the title <h1>...
      let button = createAudioButton(recordingURL, title);
      button.addEventListener("click", retrieveListOfSpeakers);
    })
    .catch(() => {
      // TODO: display an error message?
    });
}

/**
 * Sets up the (rudimentary) audio link on page load.
 */
function setupCorpusOnPageLoad() {
  let title = document.getElementById("head");
  if (!title) {
    // Could not find a head on the page.
    return;
  }

  // TODO: setup baseURL from <link rel=""> or something.
  let wordform = getEntryHead();

  fetchCorpusURL(wordform, true)
    .then((corpusURL) => {
      if (corpusURL === undefined) {
        // Corpus has nothing for this wordform ¯\_(ツ)_/¯
        return;
      }

      createCorpusButton(corpusURL, title);
    })
    .catch(() => {
      // TODO: display an error message?
    });
}

/**
 * Makes all URL paths relative to '/'.
 * In development, the root path is '/', so nothing changes.
 * On Sapir (as of 2020-03-09), the root path is '/dictionary/'.
 */
function makeRouteRelativeToSlash(route) {
  let baseURL = Urls["dictionary-index"]();
  return route.replace(baseURL, "/");
}

/**
 * Returns the head of the current dictionary entry on a /word/* page.
 */
function getEntryHead() {
  let dataElement = document.getElementById("data:head");
  return dataElement.value;
}

/**
 * Creates the 🔊 button and places it beside the desired element.
 */
function createAudioButton(recordingURL, element) {
  let recording = new Audio(recordingURL);
  recording.preload = "none";

  let template = document.getElementById("template:play-button");

  let fragment = template.content.cloneNode(true);
  let button = fragment.querySelector("button");
  button.addEventListener("click", () => recording.play());

  // Place "&nbsp;<button>...</button>"
  // at the end of the element
  let nbsp = document.createTextNode(NO_BREAK_SPACE);
  element.appendChild(nbsp);
  element.appendChild(button);

  return button;
}

/**
 * Creates the 📚 button and places it beside the desired element.
 */
function createCorpusButton(href, element) {
  let template = document.getElementById("template:corpus-button");

  let fragment = template.content.cloneNode(true);
  let button = fragment.querySelector("a");
  button.href = href;
  let nbsp = document.createTextNode(NO_BREAK_SPACE);
  element.appendChild(nbsp);
  element.appendChild(button);

  return button;
}

////////////////////// Fetch information from the page ///////////////////////

/**
 * @returns {(Element|null)}
 */
function getSearchResultList() {
  return document.getElementById("search-result-list");
}

function setupRefocus() {
  // add an action on click to refocus when data-md-focus is available
  document.querySelectorAll("[data-md-focus]").forEach((object) => {
    let focus_obj = document.getElementById(
      object.getAttribute("data-md-focus")
    );
    focus_obj.addEventListener("shown.bs.collapse", function () {
      focus_obj.scrollIntoView({
        beahior: "smooth",
        block: "start",
        inline: "start",
      });
    });
  });
}
