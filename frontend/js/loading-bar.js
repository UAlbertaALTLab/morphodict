/**
 * Manipulate the progress bar.
 */

const ERROR_CLASS = 'search-progress--error'
const LOADING_CLASS = 'search-progress--loading'

/**
 * Make a 10% progress bar. We actually don't know how much there is left,
 * but make it seem like it's thinking about it!
 */
export function indicateLoading() {
  let progress = document.getElementById('loading-indicator')
  progress.max = 100
  progress.value = 10
  progress.classList.remove(ERROR_CLASS)
  progress.classList.add(LOADING_CLASS)
}


export function indicateLoadedSuccessfully() {
  let progress = document.getElementById('loading-indicator')
  progress.value = 100
  hideLoadingIndicator()
}

export function indicateLoadingFailure() {
  // makes the loading state "indeterminate", like it's loading forever.
  let progress = document.getElementById('loading-indicator')
  progress.removeAttribute('value')
  progress.classList.add(ERROR_CLASS)
}

export function hideLoadingIndicator() {
  let progress = document.getElementById('loading-indicator')
  progress.classList.remove(LOADING_CLASS, ERROR_CLASS)
}

