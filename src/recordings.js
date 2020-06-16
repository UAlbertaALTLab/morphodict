// the specific URL for a given wordform (refactored from previous commits).
// TODO: should come from config.
const BASE_URL = 'https://sapir.artsrn.ualberta.ca/validation'

// the specific URL for a given speaker (appended with the speaker code)
const BASE_SPEAKER_URL = 'https://www.altlab.dev/maskwacis/Speakers/'

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

  let template = document.getElementById('template:recording-item')
  let recordingsList = document.querySelector('.recordings-list')

  // Request the JSON for all recordings of this wordform
  fetch(derivedURL)
    .then(request => request.json())
    .then(returnedData => {
      let numberOfRecordings = returnedData.length // number of records on the server

      // Unhide the explainer text
      let recordingsHeading = document.querySelector('.definition__recordings--not-loaded')
      recordingsHeading.classList.remove('definition__recordings--not-loaded')

      // we only want to display our list of speakers once!
      if (recordingsList.childElementCount < numberOfRecordings) {
        displaySpeakerList(returnedData)
      }
    })

  ////////////////////////////////// helpers /////////////////////////////////

  // the function that displays an individual speaker's name
  function displaySpeakerList(recordings) {
    for (let recordingData of recordings) {
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
    createdSpeakerButton.addEventListener('click', () => {
      audio.play()
      displaySpeakerBioLink(recordingData)
    })
  }

  // the function that creates a link for an individual speaker's bio to be clicked
  function displaySpeakerBioLink(recordingData) {
    // the URL to be placed into the DOM
    let insertedURL = BASE_SPEAKER_URL + recordingData['speaker'] + '.html'

    // select for the area to place the speaker link
    let container = document.querySelector('.speaker-link')

    // clone our template so we can insert it into the DOM
    let createdTemplateNode = document.getElementById('template:speaker-bio-link').content.cloneNode(true)

    // link inside the template
    let createdLink = createdTemplateNode.firstChild

    // variable (speaker's name) to be inserted into the DOM
    let speakerName = recordingData['speaker_name']

    // generate a new link and append it to the page if there isn't already one
    if (container.childElementCount < 1) {
      // set the speaker-link text with the name of the speaker
      createdTemplateNode.querySelector('slot[name="speaker-name"]').innerText = speakerName

      // set the link URL
      createdLink = createdTemplateNode.firstChild
      createdLink.href = insertedURL

      // and place the node into the DOM
      container.appendChild(createdTemplateNode)
    } else {
      // remove the node that was created:
      container.removeChild(container.childNodes[1]) // may need to extract the inner parameter based on Eddie's feedback...

      // create a new node for the new speaker name
      let newSpeakerNode = document.getElementById('template:speaker-bio-link').content.cloneNode(true)
      // ...and place the newly clicked speaker's name into it
      newSpeakerNode.querySelector('slot[name="speaker-name"]').innerText = speakerName

      // get the URL again and reinsert into the newly created node
      createdLink = newSpeakerNode.firstChild
      createdLink.href = insertedURL

      // place said node into the DOM
      container.appendChild(newSpeakerNode)
    }
  }
}

// TODOkobe: Once everything is working, play with a way to dynamically indicate (on the button) that a repeat 'speaker' is a v1, v2, v3, etc
