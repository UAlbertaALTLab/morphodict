/* global Urls:readable */
// "Urls" is a magic variable that allows use to reverse urls in javascript
// See https://github.com/ierror/django-js-reverse

import $ from 'jquery'

// Process CSS with PostCSS automatically. See rollup.config.js for more
// details.
import './css/styles.css'
import {createTooltip} from './tooltip'
import {fetchFirstRecordingURL, retrieveListOfSpeakers} from './recordings.js'
import * as orthography from './orthography.js'
import {emptyElement, removeElement, showElement, hideElement} from './dom-utils.js'
import {
  indicateLoading,
  indicateLoadedSuccessfully,
  indicateLoadingFailure,
  hideLoadingIndicator
} from './loading-bar.js'


const NO_BREAK_SPACE = '\u00A0'


/**
 * clean paradigm details
 */
function cleanParadigm() {
  removeElement(document.getElementById('paradigm'))
}


function showProse() {
  showElement(document.getElementById('prose'))
}

function hideProse() {
  hideElement(document.getElementById('prose'))
}

/**
 * find #search-result-list element on the page to attach relevant handlers to the tooltip icons
 */
function prepareTooltips() {
  const searchResultList = getSearchResultList()

  // attach handlers for tooltip icon at preverb breakdown
  let tooltips = searchResultList.querySelectorAll('.definition-title__tooltip-icon, .preverb-breakdown__tooltip-icon')
  for (let icon of tooltips) {
    createTooltip($(icon), $(icon).next('.tooltip'))
  }
}

/**
 * use AJAX to load search results in place
 *
 * @param {HTMLInputElement} searchInput
 */
function loadSearchResults(searchInput) {
  let userQuery = searchInput.value
  let searchResultList = getSearchResultList()

  if (userQuery !== '') {
    issueSearch()
  } else {
    goToHomePage()
  }

  function issueSearch() {
    let searchURL = Urls['cree-dictionary-search-results'](userQuery)

    window.history.replaceState(userQuery, document.title, urlForQuery(userQuery))
    hideProse()
    indicateLoading()

    fetch(searchURL)
      .then(response => response.text())
      .then((html) => {
        // user input may have changed during the request
        const inputNow = searchInput.value

        if (inputNow !== userQuery) {
          // input has changed, so ignore this request to prevent flashing
          // out-of-date search results
          return
        }

        // Remove loading cards
        indicateLoadedSuccessfully()
        cleanParadigm()
        searchResultList.innerHTML = html
        prepareTooltips()
      })
      .catch(() => {
        indicateLoadingFailure()
      })
  }

  function goToHomePage() {
    window.history.replaceState(userQuery, document.title, Urls['cree-dictionary-index']())

    showProse()

    hideLoadingIndicator()
    emptyElement(searchResultList)
  }

  /**
   * Returns a URL that search for the given query.
   *
   * The URL is constructed by using the <form>'s action="" attribute.
   */
  function urlForQuery(userQuery) {
    let form = searchInput.closest('form')
    return form.action + `?q=${encodeURIComponent(userQuery)}`
  }
}

/**
 * Change tab title according to user input in the search bar
 *
 * @param inputVal {string}
 */
function changeTitleBySearchQuery(inputVal) {
  setSubtitle(inputVal ? '🔎 ' + inputVal : null)
}

function setSubtitle(subtitle) {
  let defaultTitle = 'itwêwina: the online Cree dictionary'
  document.title = subtitle ? `${subtitle} — ${defaultTitle}` : defaultTitle
}

/**
 * Sets up the (rudimentary) audio link on page load.
 */
function setupAudioOnPageLoad() {
  let title = document.getElementById('head')
  if (!title) {
    // Could not find a head on the page.
    return
  }

  // TODO: setup baseURL from <link rel=""> or something.
  let template = document.getElementById('template:play-button')
  let wordform = getEntryHead()

  fetchFirstRecordingURL(wordform)
    .then((recordingURL) => {
      let recording = new Audio(recordingURL)
      recording.preload = 'none'

      let fragment = template.content.cloneNode(true)
      // Place "&nbsp;<button>...</button>"
      // at the end of the <h1?
      // TODO: it shouldn't really be **inside** the <h1>...
      let button = fragment.childNodes[0]
      let nbsp = document.createTextNode(NO_BREAK_SPACE)
      title.appendChild(nbsp)
      title.appendChild(button)
      button.addEventListener('click', () => recording.play())
      button.addEventListener('click', retrieveListOfSpeakers)
    })
    .catch(() => {
      // TODO: display an error message?
    })
}

/**
 * Makes all URL paths relative to '/'.
 * In development, the root path is '/', so nothing changes.
 * On Sapir (as of 2020-03-09), the root path is '/cree-dictionary/'.
 */
function makeRouteRelativeToSlash(route) {
  let baseURL = Urls['cree-dictionary-index']()
  return route.replace(baseURL, '/')
}

/**
 * Returns the head of the current dictionary entry on a /word/* page.
 */
function getEntryHead() {
  let dataElement = document.getElementById('data:head')
  return dataElement.value
}

document.addEventListener('DOMContentLoaded', () => {
  // XXX: HACK! reloads the site when the back button is pressed.
  window.onpopsate = () => location.reload()

  let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value
  orthography.registerEventListener(csrfToken)

  setupSearchBar()

  let route = makeRouteRelativeToSlash(window.location.pathname)
  // Tiny router.
  if (route === '/') {
    // Homepage
    setSubtitle(null)
  } else if (route === '/about') {
    // About page
    setSubtitle('About')
  } else if (route == '/contact-us') {
    // Contact page
    setSubtitle('Contact us')
  } else if (route === '/search') {
    // Search page
    prepareTooltips()
  } else if (route.match(/^[/]word[/].+/)) {
    // Word detail/paradigm page. This one has the 🔊 button.
    setSubtitle(getEntryHead())
    setupAudioOnPageLoad()
  } else {
    throw new Error(`Could not match route: ${route}`)
  }
})

function setupSearchBar() {
  let searchBar = document.getElementById('search')
  searchBar.addEventListener('input', () => {
    let query = searchBar.value
    loadSearchResults(searchBar)
    changeTitleBySearchQuery(query)
  })
}

////////////////////// Fetch information from the page ///////////////////////

/**
 * @returns {(Element|null)}
 */
function getSearchResultList() {
  return document.getElementById('search-result-list')
}
