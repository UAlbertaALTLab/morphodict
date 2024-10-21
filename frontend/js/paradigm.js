/**
 * Set up any page that has the #paradigm element with its size controls.
 */
import { loadParadigmAudio } from "./paradigm-recording";

export function setupParadigm() {
  setupParadigmSizeToggleButton(null);
}

let paradigmSizes;

/**
 * attach handlers to the "show more/less" button. So that it:
 *
 *  - loads a more detailed paradigm when clicked or do nothing and report to console if the request for the paradigm errors
 *  - changes its text to "show less" when the paradigm has the largest size
 *    and shows the smallest paradigm when clicked
 *  - prepare the new "show more/less" button to do these 3
 */
function setupParadigmSizeToggleButton(currentParadigmSize) {
  const toggleButton = document.querySelector(".js-paradigm-size-button");

  if (!toggleButton) {
    // There's nothing to toggle, hence nothing to setup. Done!
    return;
  }

  // `lemmaId` should be embedded by Django into the template.
  // It's present when the current page is lemma detail/paradigm page
  const lemmaId = readDjangoJsonScript("lemma-id");
  // `paradigmSize` is also rendered by a Django template
  // And it can changed dynamically by JavaScript when the script loads different sized paradigms
  let paradigmSize =
    currentParadigmSize || readDjangoJsonScript("paradigm-size");
  paradigmSizes = readDjangoJsonScript("paradigm-sizes") || [];

  if (paradigmSizes.length <= 1) {
    toggleButton.remove();
    return;
  }

  const nextParadigmSize = getNextParadigmSize(paradigmSize);

  toggleButton.addEventListener("click", () => {
    displayButtonAsLoading(toggleButton);

    fetch(
      window.Urls["morphodict-paradigm-detail"]() +
        `?lemma-id=${lemmaId}&paradigm-size=${nextParadigmSize}`
    )
      .then((r) => {
        if (r.ok) {
          return r.text();
        } else {
          // TODO: show error on the loading component
          throw new Error(
            `${r.status} ${r.statusText} when loading paradigm: ${r.text()}`
          );
        }
      })
      .then((text) => {
        const newParadigm = document
          .createRange()
          .createContextualFragment(text);

        // TODO: the backend should SOLELY maintain this:
        if (mostDetailedParadigmSizeIsSelected()) {
          setParadigmSizeToggleButtonText("-", "show less");
        } else {
          setParadigmSizeToggleButtonText("+", "show more");
        }

        const paradigmContainer = document.getElementById("paradigm");
        paradigmContainer
          .querySelector(".js-replaceable-paradigm")
          .replaceWith(newParadigm);

        paradigmSize = nextParadigmSize;
        setupParadigmSizeToggleButton(paradigmSize);
        updateCurrentURLWithParadigmSize();

        function setParadigmSizeToggleButtonText(symbol, text) {
          newParadigm.querySelector(".js-button-text").textContent = text;
          newParadigm.querySelector(".js-plus-minus").textContent = symbol;
        }
        loadParadigmAudio();
      })
      .catch((err) => {
        displayButtonAsError(toggleButton);
        console.error(err);
      });
  });

  function mostDetailedParadigmSizeIsSelected() {
    return paradigmSizes.indexOf(nextParadigmSize) === paradigmSizes.length - 1;
  }

  function updateCurrentURLWithParadigmSize() {
    window.history.replaceState(
      {},
      document.title,
      updateQueryParam("paradigm-size", nextParadigmSize)
    );
  }
}

/**
 * Make the button look like it's loading.
 */
function displayButtonAsLoading(toggleButton) {
  toggleButton.classList.add("paradigm__size-toggle-button--loading");
}

/**
 * Make the button look like something went wrong.
 */
function displayButtonAsError(toggleButton) {
  toggleButton.classList.remove("paradigm__size-toggle-button--loading");
  // TODO: should have an error state for the toggle button!
}

/**
 * cycles between BASIC, FULL, LINGUISTIC
 *
 * @param {String} size
 * @return {String}
 */
function getNextParadigmSize(sizeName) {
  const index = paradigmSizes.indexOf(sizeName);
  if (index >= 0) {
    return paradigmSizes[(index + 1) % paradigmSizes.length];
  }
  // Use default.
  return paradigmSizes[0];
}

///////////////////////////// Internal functions /////////////////////////////

/**
 * Read JSOn data produced by Django's `json_script` filter during HTML template generation
 */
function readDjangoJsonScript(id) {
  const jsonScriptElement = document.getElementById(id);
  if (jsonScriptElement) {
    return JSON.parse(jsonScriptElement.textContent);
  } else {
    return undefined;
  }
}

/**
 * Update the current query parameters.
 * Derived from: https://stackoverflow.com/a/41542008/6626414
 */
function updateQueryParam(key, value) {
  let search = new URLSearchParams(window.location.search);
  search.set(key, value);

  let url = new URL(window.location.href);
  url.search = search.toString();

  return url.href;
}
