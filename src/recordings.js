import SimpleTemplate from './simple-template.js'



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
 * Render a list of speakers (in the form of a select) for the user to interact with and hear the wordform pronounced in different ways.
 */
export function retrieveListOfSpeakers() {
  // get the value of the wordform from the page
  let wordform = document.getElementById('data:head').value
  let derivedURL = `${BASE_URL}/recording/_search/${wordform}`

  let recordingsList = document.querySelector('.recordings-list') // to be deleted, but not yet because it'll break the refactoring 💀
  
  // select for our elements for playback and link-generation
  let recordingsDropdown = document.getElementById('recordings-dropdown')
  let recordingsPlayback = document.getElementById('selected-speaker-playback')
  let recordingsLink = document.getElementById('selected-speaker-external-link')


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
      let individualSpeaker = SimpleTemplate.fromId('template:recording-item')
      // put the list item into the DOM
      setupButton(individualSpeaker, recordingData)
      recordingsList.appendChild(individualSpeaker.element)
    }
  }

  function setupButton(createdSpeakerButton, recordingData) {
    // Add appropriate text
    createdSpeakerButton.slot['speaker-name'] = recordingData['speaker_name']
    // TODO: this should be derived from the recording JSON
    // TODO: as of 2020-06-04, it does not include this data :(
    createdSpeakerButton.slot['speaker-dialect'] = recordingData['dialect']

    // Setup audio
    let audio = new Audio(recordingData.recording_url)
    audio.preload = 'none'
    createdSpeakerButton.element.addEventListener('click', () => {
      audio.play()
      displaySpeakerBioLink(recordingData)
    })
  }

  // the function that creates a link for an individual speaker's bio to be clicked
  function displaySpeakerBioLink(recordingData) {
    // the URL to be placed into the DOM
    let insertedURL = recordingData['speaker_bio_url']

    // select for the area to place the speaker link
    let container = document.querySelector('.speaker-link')

    // variable (speaker's name) to be inserted into the DOM
    let speakerName = recordingData['speaker_name']

    // generate a new link and append it to the page if there isn't already one
    if (container.childElementCount < 1) {
      // clone our template so we can insert it into the DOM
      let createdLink = SimpleTemplate.fromId('template:speaker-bio-link')

      // set the speaker-link text with the name of the speaker
      createdLink.slot['speaker-name'] = speakerName

      // set the link URL
      createdLink.element.href = insertedURL

      // and place the node into the DOM
      container.appendChild(createdLink.element)
    } else {
      // remove the node that was created:
      container.removeChild(container.childNodes[1]) // may need to extract the inner parameter based on Eddie's feedback...

      // create a new node for the new speaker name
      let newSpeakerNode = SimpleTemplate.fromId('template:speaker-bio-link')
      // ...and place the newly clicked speaker's name into it
      newSpeakerNode.slot['speaker-name'] = speakerName

      // get the URL again and reinsert into the newly created node
      newSpeakerNode.element.href = insertedURL

      // place said node into the DOM
      container.appendChild(newSpeakerNode.element)
    }
  }
}
