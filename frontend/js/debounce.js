/**
 * A debounce function. Documentation: https://davidwalsh.name/javascript-debounce-function
 * @param  {Function} func      The function to debounce
 * @param  {Number}   wait      The time to wait, in milliseconds
 * @param  {Boolean}  immediate Whether to invoke the function immediately
 * @return {Function}
 */
export function debounce(func, wait, immediate) {

  let timeout

  return function debounced(...args) {

    const later = () => {
      timeout = null
      if (!immediate) func.apply(this, args)
    }

    const callNow = immediate && !timeout

    clearTimeout(timeout)
    timeout = setTimeout(later, wait)

    if (callNow) func.apply(this, args)

  }
}

