import SimpleTemplate from "./simple-template.js";

// the specific URL for a given wordform (refactored from previous commits).
// TODO: should come from config.
const BASE_URL = "https://speech-db.altlab.app";

export function fetchRecordings(wordform) {
  return fetch(`${BASE_URL}/recording/_search/${wordform}`).then(function (
    response
  ) {
    return response.json();
  });
}

export async function fetchFirstRecordingURL(wordform) {
  let results = await fetchRecordings(wordform);
  return results[0]["recording_url"];
}

/**
 * Fetches recordings URLs for each wordform given.
 *
 * @param {Iterable<str>} iterable of wordforms to search
 * @return {Map<str, str>} maps wordforms to a valid recording URL.
 */
export async function fetchRecordingURLForEachWordform(requestedWordforms) {
  let wordform2recordingURL = new Map();

  const endpoint = "https://speech-db.altlab.app/api/bulk_search";
  let searchParams = new URLSearchParams();
  for (let wordform of requestedWordforms) {
    searchParams.append("q", wordform);
  }

  let url = new URL(endpoint);
  url.search = searchParams;

  let response = await fetch(url);
  if (!response.ok) {
    throw new Error("No recordings");
  }

  let data = await response.json();

  for (let recording of data.matched_recordings) {
    let wordform = recording.wordform;

    if (wordform2recordingURL.has(wordform)) {
      // Already have the first recording for this.
      continue;
    }

    wordform2recordingURL.set(wordform, recording.recording_url);
  }

  return wordform2recordingURL;
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
