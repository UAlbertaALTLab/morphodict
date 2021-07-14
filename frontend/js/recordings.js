import SimpleTemplate from "./simple-template.js";

// the specific URL for a given wordform (refactored from previous commits).
// TODO: should come from config.
const BASE_URL = "https://speech-db.altlab.app";
const BULK_API_URL = `${BASE_URL}/api/bulk_search`;

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
 * Render a list of speakers (in the form of a select) for the user to interact with and hear the wordform pronounced in different ways.
 */
export function retrieveListOfSpeakers() {
  // get the value of the wordform from the page
  let wordform = document.getElementById("data:head").value;
  let derivedURL = `${BASE_URL}/recording/_search/${wordform}`;

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

  // Request the JSON for all recordings of this wordform
  fetch(derivedURL)
    .then((request) => request.json())
    .then((returnedData) => {
      // Unhide the explainer text
      let recordingsHeading = document.querySelector(
        ".definition__recordings--not-loaded"
      );
      recordingsHeading.classList.remove("definition__recordings--not-loaded");

      // display our list of speakers
      displaySpeakerList(returnedData);
    });

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

/**
 * Uses speech-db's bulk API to search for recordsings.
 *
 * @param {Iterable<str>}  one or more wordforms to search for.
 * @return {BulkSearchResponse} see API documentation: TODO
 */
async function fetchRecordingUsingBulkSearch(requestedWordforms) {
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
