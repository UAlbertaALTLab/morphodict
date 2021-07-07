/**
 * Sets up all <form data-save-preference> elements on the page to be submitted upon
 * change. This means there is no need for a submit <button> in the form as
 * changes are persisted when they're made.
 *
 * Assumes at least the HTML that looks like this:
 *
 * <form data-save-preference action="url/to/valid/action" method="POST">
 *  <input name="setting" value="value1">
 *  <input name="setting" value="value2">
 *  <input name="setting" value="value3">
 * </form>
 *
 * A <button type="submit"> is removed from the form, if it exists.
 */
export function setupAutoSubmitForEntirePage() {
  let forms = document.querySelectorAll('form[data-save-preference]')
  for (const form of forms) {
    setupFormAutoSubmit(form)
  }
}

/**
 * Enables save preference on change.
 *
 * @param {HTMLFormElement} the form that has all of the information.
 */
function setupFormAutoSubmit(form) {
  const endpoint = form.action
  const submitButton = form.querySelector('button[type=submit]')

  form.addEventListener('change', () => void changePreference())

  if (submitButton) {
    submitButton.remove()
  }

  /////////////////////////////// Utilities ////////////////////////////////

  async function changePreference() {
    let response = await fetch(endpoint, {
      method: 'POST',
      body: new FormData(form)
    })

    return response.ok ? Promise.resolve() : Promise.reject()
  }
}
