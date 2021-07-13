// "Urls" is a magic variable that allows use to reverse urls in javascript
// See https://github.com/ierror/django-js-reverse

// Process CSS with PostCSS automatically. See rollup.config.js for more
// details.
import "./css/styles.css";
import { createTooltip } from "./js/tooltip";
import {
  fetchFirstRecordingURL,
  retrieveListOfSpeakers,
} from "./js/recordings.js";
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
const SERACH_BAR_DEBOUNCE_TIME = 450;

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
  } else if (route.match(/^[/]word[/].+/)) {
    // Word detail/paradigm page. This one has the 🔊 button.
    setSubtitle(getEntryHead());
    setupAudioOnPageLoad();
    setupParadigm();
    prepareTooltips();
  }
});

function setupSearchBar() {
  const searchBar = document.getElementById("search");
  const debouncedLoadSearchResults = debounce(() => {
    loadSearchResults(searchBar);
  }, SERACH_BAR_DEBOUNCE_TIME);

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

  let wordform2recordingURL = new Map();

  let searchParams = new URLSearchParams();
  for (let wordform of requestedWordforms) {
    searchParams.append("q", wordform);
  }
  const endpoint = "https://speech-db.altlab.app/api/bulk_search";
  let url = new URL(endpoint);
  url.search = searchParams;

  let data;
  if (0) {
    let resp = await fetch(url);
    if (!resp.ok) {
      // Fail silently ¯\_(ツ)_/¯
      return;
    }
    data = await response.json();
  } else {
    data = {
      matched_recordings: [
        {
          wordform: "wâpamêw",
          speaker: "HAR",
          speaker_name: "Harley Simon",
          anonymous: false,
          gender: "M",
          dialect: "Maskwacîs",
          recording_url:
            "http://speech-db.altlab.app/media/audio/da213e0ac776a153030a87c1c47bc7e0d24a91233d9a1fa1e32d4b04cb383b65_fdqRrHt.m4a",
          speaker_bio_url: "https://www.altlab.dev/maskwacis/Speakers/HAR.html",
        },
        {
          wordform: "wâpamêw",
          speaker: "HAR",
          speaker_name: "Harley Simon",
          anonymous: false,
          gender: "M",
          dialect: "Maskwacîs",
          recording_url:
            "http://speech-db.altlab.app/media/audio/8efae63b40e1bc44c37515ec56121bc734e2cb11d90c59d71f6d847dc6f82ac3_bM2P2A6.m4a",
          speaker_bio_url: "https://www.altlab.dev/maskwacis/Speakers/HAR.html",
        },
        {
          wordform: "wâpamêw",
          speaker: "HAR",
          speaker_name: "Harley Simon",
          anonymous: false,
          gender: "M",
          dialect: "Maskwacîs",
          recording_url:
            "http://speech-db.altlab.app/media/audio/79d38cc7e67e73a50cb91f8d93fe96212c906d18b404f6d91412f6f7508c56c4_8csquYb.m4a",
          speaker_bio_url: "https://www.altlab.dev/maskwacis/Speakers/HAR.html",
        },
        {
          wordform: "asawâpamêw",
          speaker: "ANN",
          speaker_name: "Annette Lee",
          anonymous: false,
          gender: "F",
          dialect: "Maskwacîs",
          recording_url:
            "http://speech-db.altlab.app/media/audio/329a115f1ddef1c8a7a4003136e198c49878f96add1895f7a383cf45a331a153_uMOIs5J.m4a",
          speaker_bio_url: "https://www.altlab.dev/maskwacis/Speakers/ANN.html",
        },
        {
          wordform: "asawâpamêw",
          speaker: "ANN",
          speaker_name: "Annette Lee",
          anonymous: false,
          gender: "F",
          dialect: "Maskwacîs",
          recording_url:
            "http://speech-db.altlab.app/media/audio/0307dedb9a095057765dfb3336d50ea5ebf91283ed0aa5aad70b76068c3ac25f_wv6NXWw.m4a",
          speaker_bio_url: "https://www.altlab.dev/maskwacis/Speakers/ANN.html",
        },
        {
          wordform: "asawâpamêw",
          speaker: "BET",
          speaker_name: "Betty Simon",
          anonymous: false,
          gender: "F",
          dialect: "Maskwacîs",
          recording_url:
            "http://speech-db.altlab.app/media/audio/3b6d20696f22ca8fc568d27019b6c2993d2e419b2d4b4dfcddc91e5be9b9eb42_2dBElHQ.m4a",
          speaker_bio_url: "https://www.altlab.dev/maskwacis/Speakers/BET.html",
        },
        {
          wordform: "asawâpamêw",
          speaker: "BET",
          speaker_name: "Betty Simon",
          anonymous: false,
          gender: "F",
          dialect: "Maskwacîs",
          recording_url:
            "http://speech-db.altlab.app/media/audio/11169a4cd2588ca469ff553fce232460aa7e65f22586d9e4daf80d3f2f31c73f_bSvEpkh.m4a",
          speaker_bio_url: "https://www.altlab.dev/maskwacis/Speakers/BET.html",
        },
      ],
      not_found: [],
    };
  }

  for (let recording of data.matched_recordings) {
    let wordform = recording.wordform;

    if (wordform2recordingURL.has(wordform)) {
      // Already have the first recording for this.
      continue;
    }

    wordform2recordingURL.set(wordform, recording.recording_url);
  }

  for (let [element, wordform] of elementWithWordform) {
    let recordingURL = wordform2recordingURL.get(wordform);
    if (recordingURL) {
      createAudioButton(recordingURL, element);
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
    let searchURL = Urls["cree-dictionary-search-results"](userQuery);

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
    window.history.replaceState(null, "", Urls["cree-dictionary-index"]());

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

function setSubtitle(subtitle) {
  let defaultTitle = "itwêwina: the online Cree dictionary";
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
      // TODO: it shouldn't be placed be **inside** the title <h1>...
      let button = createAudioButton(recordingURL, title);
      button.addEventListener("click", retrieveListOfSpeakers);
    })
    .catch(() => {
      // TODO: display an error message?
    });
}

/**
 * Makes all URL paths relative to '/'.
 * In development, the root path is '/', so nothing changes.
 * On Sapir (as of 2020-03-09), the root path is '/cree-dictionary/'.
 */
function makeRouteRelativeToSlash(route) {
  let baseURL = Urls["cree-dictionary-index"]();
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

////////////////////// Fetch information from the page ///////////////////////

/**
 * @returns {(Element|null)}
 */
function getSearchResultList() {
  return document.getElementById("search-result-list");
}
