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
      let speakerURLIndexCount = 0

      while (speakerURLIndexCount < numberOfRecordings) {
        // Create the list element
        let individualSpeaker = template.content.firstChild.cloneNode(true)
        // put the list item into the DOM
        recordingsList.appendChild(individualSpeaker)

        speakerURLIndexCount++
      }

      // TODOkobe: hey future Eddie (+ Kobe), should the for-loop be within the while loop above?

      /**
      * Add text to the newly created buttons with a for-loop and get audio playback for each button
      */
      for (let speakerURLIndexCount = 0; speakerURLIndexCount < firstJSONData.length; speakerURLIndexCount++) {

        // select for the buttons...
        let createdSpeakerButtons = document.querySelectorAll('button.audio-snippet')
        let createdSpeakerButton = createdSpeakerButtons[speakerURLIndexCount]

        // ...and then iterate through them to add text
        createdSpeakerButton.querySelector('slot[name="speaker-name"]')
          .innerText = firstJSONData[speakerURLIndexCount]['speaker_name']
        // TODO: this should be derived from the recording JSON
        // TODO: as of 2020-06-04, it does not include this data :(
        createdSpeakerButton.querySelector('slot[name="speaker-dialect"]')
          .innerText = 'Maskwacîs'

        // put an event listener on the button: the event is the URL playback
        createdSpeakerButton.addEventListener('click', function() {
          var audio = new Audio(firstJSONData[speakerURLIndexCount].recording_url)
          audio.type = 'audio/m4a'
          audio.play()

        })
      }
    }
  }

  // send the request!
  xhttp.send()
}

// TODOkobe: Once everything is working, play with a way to dynamically indicate (on the button) that a repeat 'speaker' is a v1, v2, v3, etc
