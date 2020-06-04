// the specific URL for a given wordform (refactored from previous commits).
const BASE_URL = 'http://sapir.artsrn.ualberta.ca/validation';

// the specific URL for a given speaker
const SPEAKER_URL = 'http://altlab.ualberta.ca/maskwacis/Speakers/';

export function fetchRecordings(wordform) {
  // TODO: should come from config.
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
  let wordform = document.getElementById('data:head').value;
  let derivedURL = `${BASE_URL}/recording/_search/${wordform}`;

  // setting up the JSON request
  let xhttp = new XMLHttpRequest();
  xhttp.open('GET', derivedURL, true);

  // receiving request information from SAPIR
  xhttp.onload = function() {
    let returnedData = JSON.parse(this.response); // response from the server
    let numberOfRecordings = returnedData.length; // number of records on the server
    let recordingsList = document.querySelector('.recordings-list');
    let recordingsHeading = document.querySelector('.definition__recordings');
    
    // we only want to display our list of speakers once!
    if (recordingsList.childElementCount < numberOfRecordings) {
      displaySpeakerList(returnedData);
    }

    // the function that displays an individual speaker's name
    function displaySpeakerList(firstJSONData) {
      recordingsHeading.insertAdjacentHTML('afterbegin', '<h3 class="explainer">Select a name below to hear the word above said by different speakers. <br> (See a speaker\'s name more than once? The same speaker pronounces the word in different ways!)</h3>');
      
      let speakerURLIndexCount = 0;
      let speakerCodeArray = new Array(firstJSONData.length);

      while (speakerURLIndexCount < numberOfRecordings) {
        // create a list element and set an attribute on it for testing
        let individualSpeaker = document.createElement('li');
        individualSpeaker.classList.add('recordings-list__item');
        individualSpeaker.setAttribute('data-cy', 'recordings-list__item');

        // create a button element: add a class to it for future styling needs
        let speakerButton = document.createElement('button');
        speakerButton.classList.add('audio-snippet');

        // put the button into the list
        individualSpeaker.appendChild(speakerButton);

        // put the list into the DOM
        recordingsList.appendChild(individualSpeaker);

        speakerURLIndexCount++;
      }

      // TODOkobe: hey future Eddie (+ Kobe), should the for-loop be within the while loop above?

      /**
      * Add text to the newly created buttons with a for-loop and get audio playback for each button
      */
      for (let speakerURLIndexCount = 0; speakerURLIndexCount < firstJSONData.length; speakerURLIndexCount++) {

        // select for the buttons...
        let createdSpeakerButton = document.querySelectorAll('button.audio-snippet');

        // ...and then iterate through them to add text
        createdSpeakerButton[speakerURLIndexCount].innerText = firstJSONData[speakerURLIndexCount].speaker_name + ', Maskwacîs';

        // put the speaker name and speaker code into the array as an object to be worked with
        speakerCodeArray.push( {
         speaker: firstJSONData[speakerURLIndexCount].speaker,
         speaker_name: firstJSONData[speakerURLIndexCount].speaker_name
        });
        // put an event listener on the button: the event is the URL playback
        createdSpeakerButton[speakerURLIndexCount].addEventListener('click', function() {
          var audio = new Audio(firstJSONData[speakerURLIndexCount].recording_url);
          audio.type = 'audio/m4a';
          audio.play();

          // call a function to...load the speaker link in the page view: said function takes the name of the speaker that was clicked
          let passedInName = event.target.innerText.replace(', Maskwacîs', ''); // TODOkobe: give this a better variable name 🥴
          loadSpeakerLink(passedInName, speakerCodeArray);
        });
      }
    }
  }

  // send the request!
  xhttp.send();
}

function loadSpeakerLink(passedInName, speakerCodeArray) {
  let speakerCode;

  // now, give me the speaker code for the name passed in.
  for(let key in speakerCodeArray){
    if(speakerCodeArray[key].speaker_name == passedInName) {
      speakerCode = speakerCodeArray[key].speaker;
    }
  }
  console.log(`${SPEAKER_URL}${speakerCode}.html`);
}
// TODOkobe: Once everything is working, play with a way to dynamically indicate (on the button) that a repeat 'speaker' is a v1, v2, v3, etc
