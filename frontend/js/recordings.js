import SimpleTemplate from "./simple-template.js";

// the specific URL for a given wordform (refactored from previous commits).
// TODO: should come from config.
const BASE_URL = "https://speech-db.altlab.app";
const LANGUAGE_CODE = getLanguageCodeFromLocation();
const BULK_API_URL = `${BASE_URL}/${LANGUAGE_CODE}/api/bulk_search`;

function getLanguageCodeFromLocation() {
  const location = window.location.toString();
  if (location.includes(`itwewina`) || location.includes(`crk`))
    return `maskwacis`;
  if (location.includes(`itwiwina`) || location.includes(`cwd`))
    return `woodscree`;
  if (location.includes(`gunaha`) || location.includes(`srs`))
    return `tsuutina`;
  if (location.includes(`arpeng`)) return `arapaho`;
  if (location.includes(`guusaaw`) || location.includes(`hdn`)) return `haida`;
  return `maskwacis`;
}

/**
 * Fetches the recording URL for one wordform.
 *
 * @param {string} a wordform. The spelling must match *exactly* with the
 *                 speech-db's transcription.
 * @return {string?} the recording URL, if it exists, else undefined.
 */
export async function fetchFirstRecordingURL(wordform) {
  let response = await fetchRecordingUsingBulkSearch([wordform]);
  return mapWordformsToBestRecordingURL(response).get(wordform);
}

/**
 * Fetches recordings URLs for each wordform given.
 *
 * @param {Iterable<str>} iterable of wordforms to search
 * @return {Map<str, str>} maps wordforms to a valid recording URL.
 */
export async function fetchRecordingURLForEachWordform(requestedWordforms) {
  let response = await fetchRecordingUsingBulkSearch(requestedWordforms);
  return mapWordformsToBestRecordingURL(response);
}

/**
 * Render a list of speakers (in the form of a select) for the user to
 * interact with and hear the wordform pronounced in different ways.
 */
export async function retrieveListOfSpeakers() {
  // There SHOULD be a <data id="data:head" value="..."> element on the page
  // that will tell us the current wordform: get it!
  let wordform = document.getElementById("data:head").value;

  // select for our elements for playback and link-generation
  let recordingsDropdown = document.querySelector(
    ".multiple-recordings select"
  );
  let recordingsPlayback = document.querySelector(
    '[data-action="play-current-recording"]'
  );
  let recordingsLink = document.querySelector(
    '[data-action="learn-about-speaker"]'
  );

  // Get all recordings for this wordform
  let response = await fetchRecordingUsingBulkSearch([wordform]);

  displaySpeakerList(
    response["matched_recordings"].filter(
      (result) => result.wordform === wordform
    )
  );
  showRecordingsExplainerText();

  ////////////////////////////////// helpers /////////////////////////////////

  // the function that displays an individual speaker's name
  function displaySpeakerList(recordings) {
    for (let recordingData of recordings) {
      // using a template, place the speaker's name and dialect into the dropdown
      let individualSpeaker = SimpleTemplate.fromId("template:speakerList");
      individualSpeaker.slot.speakerName = recordingData.speaker_name;
      individualSpeaker.slot.speakerDialect = recordingData.dialect;
      recordingsDropdown.appendChild(individualSpeaker.element);
    }

    // audio playback for the specific speaker
    recordingsPlayback.addEventListener("click", () => {
      let speakerPosition = recordingsDropdown.selectedIndex;
      let audioURL = recordings[speakerPosition].recording_url;

      // play the audio associated with that specific index
      let audio = new Audio(audioURL);
      audio.play();
    });

    // link for the specific speaker
    recordingsLink.addEventListener("click", () => {
      let speakerPosition = recordingsDropdown.selectedIndex;
      let speakerBioLink = recordings[speakerPosition].speaker_bio_url;

      // change the URL of the selected speaker
      recordingsLink.href = speakerBioLink;
    });
  }
}

function showRecordingsExplainerText() {
  let recordingsHeading = document.querySelector(
    ".definition__recordings--not-loaded"
  );
  if (!recordingsHeading) {
    return;
  }

  recordingsHeading.classList.remove("definition__recordings--not-loaded");
}

/**
 * Uses speech-db's bulk API to search for recordsings.
 *
 * @param {Iterable<str>}  one or more wordforms to search for.
 * @return {BulkSearchResponse} see https://github.com/UAlbertaALTLab/recording-validation-interface#bulk-recording-search
 */
async function fetchRecordingUsingBulkSearch(requestedWordforms) {
  let batches = chunk(requestedWordforms);

  let allMatchedRecordings = [];
  let allNotFound = [];

  for (let batch of batches) {
    let response = await _fetchRecordingUsingBulkSearch(batch);

    response["matched_recordings"].forEach((rec) =>
      allMatchedRecordings.push(rec)
    );
    response["not_found"].forEach((rec) => allNotFound.push(rec));
  }

  return {
    matched_recordings: allMatchedRecordings,
    not_found: allNotFound,
  };
}

/**
 * ACTUALLY does one HTTP request to the speech-db.
 */
async function _fetchRecordingUsingBulkSearch(requestedWordforms) {
  // Construct the query parameters: ?q=word&q=word2&q=word3&q=...
  let searchParams = new URLSearchParams();
  for (let wordform of requestedWordforms) {
    searchParams.append("q", wordform);
  }
  let url = new URL(BULK_API_URL);
  url.search = searchParams;

  let response = await fetch(url);
  if (!response.ok) {
    throw new Error("Could not fetch recordings");
  }

  return response.json();
}

/**
 * Given a BulkSearchResponse, returns a Map of wordforms to exactly one
 * recording URL.
 *
 * @param {BulkSearchResponse} the entire response returned from the bulk
 *                             search API.
 */
function mapWordformsToBestRecordingURL(response) {
  let wordform2recordingURL = new Map();

  for (let result of response["matched_recordings"]) {
    let wordform = result["wordform"];

    if (!wordform2recordingURL.has(wordform)) {
      // Assume the first result returned is the best recording:
      wordform2recordingURL.set(wordform, result["recording_url"]);
    }
  }

  return wordform2recordingURL;
}

/**
 * Chunks the iterable into subarrays of a maximum size.

 * @param {Iterable<T>}  one or more wordforms to search for.
 * @return {Array<Array<T>}}
 */
function chunk(collection) {
  const MAX_BATCH_SIZE = 30;

  // Chunk items iteratively, sort of like packing moving boxes, adding items
  // to one box at at time until the box gets full, and then moving on to a
  // new, empty box:
  let chunks = [[]];
  for (let item of collection) {
    // invariant: the array of all chunks has at least one chunk
    let currentChunk = chunks[chunks.length - 1];

    if (currentChunk.length >= MAX_BATCH_SIZE) {
      // The current chunk is full!
      // We can't add anymore items so start a new chunk.
      currentChunk = [];
      chunks.push(currentChunk);
    }

    // invariant: currentChunk.length < batch size:
    // ∴ it's safe to add an item to the current chunk
    currentChunk.push(item);
  }

  return chunks;
}
