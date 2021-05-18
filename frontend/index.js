// the /* global blah blah */ line below works with eslint so that eslint knows these variables are from the html

// "Urls" is a magic variable that allows use to reverse urls in javascript
// See https://github.com/ierror/django-js-reverse


/* global Urls:readable */


// Process CSS with PostCSS automatically. See rollup.config.js for more
// details.
import './css/styles.css'
import {createTooltip} from './js/tooltip'
import {fetchFirstRecordingURL, retrieveListOfSpeakers} from './js/recordings.js'
import * as orthography from './js/orthography.js'
import {emptyElement, removeElement, showElement, hideElement} from './js/dom-utils.js'
import {
  indicateLoading,
  indicateLoadedSuccessfully,
  indicateLoadingFailure,
  hideLoadingIndicator
} from './js/loading-bar.js'
import {debounce} from './js/debounce.js'

///////////////////////////////// Constants //////////////////////////////////

const NO_BREAK_SPACE = '\u00A0'

/**
 * Milliseconds, we only send search requests after this long of time of inactivity has passed.
 * Prevents too many invalid requests from being sent during typing
 *
 * Check the brief blog post to read a study about people's typing speed:
 * https://madoshakalaka.github.io/2020/08/31/how-hard-should-you-debounce-on-a-responsive-search-bar.html
 * @type {number}
 */
const SERACH_BAR_DEBOUNCE_TIME = 450


//////////////////////////////// On page load ////////////////////////////////

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
  } else if (route === '/contact-us') {
    // Contact page
    setSubtitle('Contact us')
  } else if (route === '/search') {
    // Search page
    prepareSearchResults(getSearchResultList())
  } else if (route.match(/^[/]word[/].+/)) {
    // Word detail/paradigm page. This one has the 🔊 button.
    setSubtitle(getEntryHead())
    setupAudioOnPageLoad()
    setupParadigmSizeToggleButton()
  } else if (route === '/query-help' || route == '/admin/fst-tool') {
    // these pages don’t use any extra JS
  } else {
    throw new Error(`Could not match route: ${route}`)
  }
})


///////////////////////////// Internal functions /////////////////////////////

/**
 * read json data produced by django's `json_script` filter during HTML template generation
 */
function readDjangoJsonScript(id) {
  const jsonScriptElement = document.getElementById(id)
  if (jsonScriptElement) {
    return JSON.parse(jsonScriptElement.textContent)
  } else {
    return undefined
  }
}

const allParadigmSizes = ['BASIC', 'FULL', 'LINGUISTIC']


/**
 * cycles between BASIC, FULL, LINGUISTIC
 *
 * @param {String} size
 * @return {String}
 */
function getNextParadigmSize(size) {
  return allParadigmSizes[(allParadigmSizes.indexOf(size) + 1) % allParadigmSizes.length]
}

/**
 * https://stackoverflow.com/a/11654596
 * get the current url and update a query param
 *
 * @param {String} key
 * @param {String} value
 * @returns {String}
 */
function updateQueryParam(key, value) {
  let url = window.location.href
  let re = new RegExp('([?&])' + key + '=.*?(&|#|$)(.*)', 'gi'),
    hash

  if (re.test(url)) {
    if (typeof value !== 'undefined' && value !== null) {
      return url.replace(re, '$1' + key + '=' + value + '$2$3')
    } else {
      hash = url.split('#')
      url = hash[0].replace(re, '$1$3').replace(/([&?])$/, '')
      if (typeof hash[1] !== 'undefined' && hash[1] !== null) {
        url += '#' + hash[1]
      }
      return url
    }
  } else {
    if (typeof value !== 'undefined' && value !== null) {
      const separator = url.indexOf('?') !== -1 ? '&' : '?'
      hash = url.split('#')
      url = hash[0] + separator + key + '=' + value
      if (typeof hash[1] !== 'undefined' && hash[1] !== null) {
        url += '#' + hash[1]
      }
      return url
    } else {
      return url
    }
  }
}


/**
 * attach handlers to the "show more/less" button. So that it:
 *
 *  - loads a more detailed paradigm when clicked or do nothing and report to console if the request for the paradigm errors
 *  - changes its text to "show less" when the paradigm has the largest size
 *    and shows the smallest paradigm when clicked
 *  - prepare the new "show more/less" button to do these 3
 */
function setupParadigmSizeToggleButton(currentParadigmSize) {
  const toggleButton = document.querySelector('.js-paradigm-size-button')

  if (!toggleButton) {
    // There's nothing to toggle, hence nothing to setup. Done!
    return
  }

  // `lemmaId` should be embedded by Django into the template.
  // It's present when the current page is lemma detail/paradigm page
  const lemmaId = readDjangoJsonScript('lemma-id')
  // `paradigmSize` is also rendered by a Django template
  // And it can changed dynamically by JavaScript when the script loads different sized paradigms
  let paradigmSize = currentParadigmSize || readDjangoJsonScript('paradigm-size')

  const nextParadigmSize = getNextParadigmSize(paradigmSize)

  toggleButton.addEventListener('click', () => {
    displayButtonAsLoading(toggleButton)

    fetch(Urls['cree-dictionary-paradigm-detail']() + `?lemma-id=${lemmaId}&paradigm-size=${nextParadigmSize}`).then(r => {
      if (r.ok) {
        return r.text()
      } else {
        throw new Error(`${r.status} ${r.statusText} when loading paradigm: ${r.text()}`)
      }
    }).then(
      text => {
        const newParadigm = document.createRange().createContextualFragment(text)

        // TODO: is this necessary? Shouldn't the component itself know what
        // text to use?
        if (mostDetailedParadigmSizeIsSelected()) {
          setParadigmSizeToggleButtonText('-', 'show less')
        } else {
          setParadigmSizeToggleButtonText('+', 'show more')
        }

        window.history.replaceState({}, document.title, updateQueryParam('paradigm-size', nextParadigmSize))

        const paradigmContainer = document.getElementById('paradigm')
        paradigmContainer.querySelector('.js-replaceable-paradigm').replaceWith(newParadigm)

        paradigmSize = nextParadigmSize
        setupParadigmSizeToggleButton(paradigmSize)

        function setParadigmSizeToggleButtonText(symbol, text) {
          newParadigm.querySelector('.js-button-text').textContent = text
          newParadigm.querySelector('.js-plus-minus').textContent = symbol
        }
      }
    ).catch((err) => {
      displayButtonAsError(toggleButton)
      console.error(err)
    })
  })

  function mostDetailedParadigmSizeIsSelected() {
    return allParadigmSizes.indexOf(nextParadigmSize) === allParadigmSizes.length - 1
  }
}

/**
 * Make the button look like it's loading.
 */
function displayButtonAsLoading(toggleButton) {
  toggleButton.classList.add('paradigm__size-toggle-button--loading')
}

/**
 * Make the button look like something went wrong.
 */
function displayButtonAsError(toggleButton) {
  toggleButton.classList.remove('paradigm__size-toggle-button--loading')
  // TODO: should have an error state for the toggle button!
}


const debouncedLoadSearchResults = debounce(() => {
  const searchBar = document.getElementById('search')
  loadSearchResults(searchBar)
}, SERACH_BAR_DEBOUNCE_TIME)



function setupSearchBar() {
  const searchBar = document.getElementById('search')
  searchBar.addEventListener('input', () => {
    indicateLoading()
    debouncedLoadSearchResults()
  })
}

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
 * Prepares interactive elements of each search result, including:
 *  - tooltips
 *  - recordings
 *
 * @param {Element} searchResultsList
 */
function prepareSearchResults(searchResultsList) {
  prepareTooltips(searchResultsList)
  loadRecordingsForAllSearchResults(searchResultsList)
}

/**
 * Given a list of search results, this will attempt to match a recording to
 * its match wordform.
 *
 * @param {Element} searchResultsList
 */
function loadRecordingsForAllSearchResults(searchResultsList) {
  for (let result of searchResultsList.querySelectorAll('[data-wordform]')) {
    let wordform = result.dataset.wordform
    let container = result // do this reassignment because of the lexical scoping :(

    // TODO: instead of making a request for each search result,
    // TODO: use a "bulk query" option that uses one request to load all
    // TODO: this requires code in the recording-validation-interface
    fetchFirstRecordingURL(wordform)
      .then((recordingURL) => createAudioButton(recordingURL, container))
      .catch(() => {/* ignore :/ */
      })
  }
}

/**
 * Attach relevant handlers to the tooltip icons of search results.
 *
 * @param {Element} searchResultsList
 */
function prepareTooltips(searchResultsList) {
  // attach handlers for tooltip icon at preverb breakdown
  let tooltips = searchResultsList
    .querySelectorAll('[data-has-tooltip]')
  for (let icon of tooltips) {
    let tooltip = icon.nextElementSibling
    if (!tooltip.classList.contains('tooltip')) {
      throw new Error('Expected tooltip to be direct sibling of icon')
    }
    createTooltip(icon, tooltip)
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
    changeTitleBySearchQuery(userQuery)
    issueSearch()
  } else {
    goToHomePage()
  }

  function issueSearch() {
    let searchURL = Urls['cree-dictionary-search-results'](userQuery)

    window.history.replaceState(userQuery, document.title, urlForQuery(userQuery))
    hideProse()

    fetch(searchURL)
      .then(response => {
        if (response.ok) {
          return response.text()
        }
        return Promise.reject()
      })
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
        prepareSearchResults(searchResultList)
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
  let wordform = getEntryHead()

  fetchFirstRecordingURL(wordform)
    .then((recordingURL) => {
      // TODO: it shouldn't be placed be **inside** the title <h1>...
      let button = createAudioButton(recordingURL, title)
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

/**
 * Creates the 🔊 button and places it beside the desired element.
 */
function createAudioButton(recordingURL, element) {
  let recording = new Audio(recordingURL)
  recording.preload = 'none'

  let template = document.getElementById('template:play-button')

  let fragment = template.content.cloneNode(true)
  let button = fragment.querySelector('button')
  button.addEventListener('click', () => recording.play())

  // Place "&nbsp;<button>...</button>"
  // at the end of the element
  let nbsp = document.createTextNode(NO_BREAK_SPACE)
  element.appendChild(nbsp)
  element.appendChild(button)

  return button
}

////////////////////// Fetch information from the page ///////////////////////

/**
 * @returns {(Element|null)}
 */
function getSearchResultList() {
  return document.getElementById('search-result-list')
}
