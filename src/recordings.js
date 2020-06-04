// the specific URL for a given wordform (refactored from previous commits).
// TODO: should come from config.
const BASE_URL = 'https://sapir.artsrn.ualberta.ca/validation'

export function fetchRecordings(wordform) {
  return fetch(`${BASE_URL}/recording/_search/${wordform}`)
    .then(function (response) {
      return response.json()
    })
}

export async function fetchFirstRecordingURL(wordform) {
  let results = await fetchRecordings(wordform)
  return results[0]['recording_url']
}


/**
 * Render a list of speakers (in button form) for the user to interact with and hear the wordform pronounced in different ways.
 */
export function retrieveListOfSpeakers() {
  // get the value of the wordform from the page
  let wordform = document.getElementById('data:head').value
  let derivedURL = `${BASE_URL}/recording/_search/${wordform}`

  // setting up the JSON request
  let xhttp = new XMLHttpRequest()
  xhttp.open('GET', derivedURL, true)

  // receiving request information from SAPIR
  xhttp.onload = function() {
    let returnedData = JSON.parse(this.response) // response from the server
    let numberOfRecordings = returnedData.length // number of records on the server
    let recordingsList = document.querySelector('.recordings-list')

    // Unhide the explainer text
    let recordingsHeading = document.querySelector('.definition__recordings--not-loaded')
    recordingsHeading.classList.remove('definition__recordings--not-loaded')

    let template = document.getElementById('template:recording-item')

    // we only want to display our list of speakers once!
    if (recordingsList.childElementCount < numberOfRecordings) {
      displaySpeakerList(returnedData)
    }

    // the function that displays an individual speaker's name
    function displaySpeakerList(firstJSONData) {
      for (let recordingData of firstJSONData) {
        // Create the list element
        let individualSpeaker = template.content.firstChild.cloneNode(true)
        // put the list item into the DOM
        recordingsList.appendChild(individualSpeaker)
        setupButton(individualSpeaker, recordingData)
      }
    }

    function setupButton(createdSpeakerButton, recordingData) {
      // Add appropriate text
      createdSpeakerButton.querySelector('slot[name="speaker-name"]')
        .innerText = recordingData['speaker_name']
      // TODO: this should be derived from the recording JSON
      // TODO: as of 2020-06-04, it does not include this data :(
      createdSpeakerButton.querySelector('slot[name="speaker-dialect"]')
        .innerText = 'Maskwacîs'

      // Setup audio
      let audio = new Audio(recordingData.recording_url)
      audio.preload = 'none'
      createdSpeakerButton.addEventListener('click', () => audio.play())
    }
  }

  // send the request!
  xhttp.send()
}

// TODOkobe: Once everything is working, play with a way to dynamically indicate (on the button) that a repeat 'speaker' is a v1, v2, v3, etc
