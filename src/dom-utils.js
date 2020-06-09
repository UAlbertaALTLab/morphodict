/**
 * A few utilites for manipulating DOM Element and Node instances.
 *
 * Intended to replace jQuery.
 *
 * See: http://youmightnotneedjquery.com/
 */

/**
 * Removes all children of an element.
 *
 * @param {Element} element
 */
export function emptyElement(element) {
  // Uses the fastest method tested here:
  // https://jsperf.com/innerhtml-vs-removechild/15
  while (element.lastChild) {
    element.removeChild(element.lastChild)
  }
}

/**
 * Removes this element from the DOM
 *
 * @param {(Element|null)} element
 */
export function removeElement(element) {
  if (!element)
    return

  let parent = element.parentNode
  parent.removeChild(element)
}

/**
 * Restores the elements display value to its default, effectively showing it
 * if it was hidden with hideElement().
 *
 * @param {(Element|null)} element
 */
export function showElement(element) {
  if (!element)
    return

  element.style.display = ''
}

/**
 * Sets the element to display: none.
 *
 * @param {(Element|null)} element
 */
export function hideElement(element) {
  if (!element)
    return

  element.style.display = 'none'
}
