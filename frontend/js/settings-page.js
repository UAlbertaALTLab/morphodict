/**
 * Sets up all <form data-save-preference> elements on the page to be submitted upon change.
 *
 * Assumes at least the HTML that looks like this:
 *
 * <form data-save-preference action="url/to/valid/action" method="POST">
 *  <input name="setting" value="value1">
 *  <input name="setting" value="value2">
 *  <input name="setting" value="value3">
 * </form>
 */
export function setupAll() {
  let forms = document.querySelectorAll('form[data-save-preference]')
  for (const form of forms) {
    setupSavePreference(form)
  }
}

/**
 * @param {HTMLFormElement} the form that has all of the information.
 */
function setupSavePreference(form) {
  const submitButton = form.querySelector('button[type=submit]')
  const endpoint = form.action

  form.addEventListener('change', () => void changePreference())

  if (submitButton) {
    submitButton.remove()
  }

  /////////////////////////////// utilities ////////////////////////////////

  async function changePreference() {
    let response = await fetch(endpoint, {
      method: 'POST',
      body: new FormData(form)
    })

    return response.ok ? Promise.resolve() : Promise.reject()
  }
}
