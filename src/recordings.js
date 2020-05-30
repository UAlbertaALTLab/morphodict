// TODO: pull out BASE_URL and declare it as a const to be used by fetchRecordings, getSpeakerList, etc...AFTER THE TEST PASSES!!!

// TODO: previously, the assumption was: one speaker has one URL associated with them and we'll use the speaker name to be our reference point for building our list. NOW, this assumption breaks when one speaker has multiple URLs associated with them. instead, we'll go with the URLs as the reference point: one URL has one speaker associated with it (so as a rough off the top example, "for every URL, give us the speaker name associated with it"). this is important because if the base URL changes, this breaks things. the way it is presently _may_ circumvent that, but not by much...

// TODO: Once everything is working, play with a way to dynamically indicate (on the button) that a repeat 'speaker' is a v1, v2, v3, etc

export function fetchRecordings(wordform) {
  // TODO: should come from config.
  const BASE_URL = '//sapir.artsrn.ualberta.ca/validation'
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
 * Render a list of speakers (in button form) for the user to interact with.
 */
export function getSpeakerList() {
  // get the value of the wordform from the page
  let wordform = document.getElementById('data:head').value;
  const BASE_URL = 'http://sapir.artsrn.ualberta.ca/validation/recording/_search/' + `${wordform}`;

  // setting up the JSON request
  let xhttp = new XMLHttpRequest();
  xhttp.open('GET', BASE_URL, true);

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
      recordingsHeading.insertAdjacentHTML('afterbegin', '<h3 class="explainer">Select a name below to hear the word above said by different speakers.</h3>');
      
      let speakerURLIndexCount = 0;

      // so to access the JSON data's URL property, I need to use firstJSONData[x].recording_url

      while (speakerURLIndexCount < numberOfRecordings) {
        // create a list element and a button; set an attribute on the former for testing
        let individualSpeaker = document.createElement('li');
        individualSpeaker.classList.add('recordings-list__item');
        individualSpeaker.setAttribute('data-cy', 'recordings-list__item');

        let speakerButton = document.createElement('button');
        speakerButton.classList.add('audio-snippet');
        
        // // put an event listener on the button (but maybe this happens after the loop)

        //    - the event is the URL playback

        // the text on the button should be the name property of the object associated with the recording_url

        // put the button into the list
        individualSpeaker.appendChild(speakerButton);

        // put the list into the DOM
        recordingsList.appendChild(individualSpeaker);

        speakerURLIndexCount++;
      }

      // at present, this happens after the button is created: is there value in moving it into the while loop above? maybe after the demo this can be refactored/cleaned up a bit
      for (let speakerURLIndexCount = 0; speakerURLIndexCount < firstJSONData.length; speakerURLIndexCount++) {
        // for testing purposes
        // console.log(firstJSONData[speakerURLIndexCount].recording_url);
        let createdSpeakerButton = document.querySelectorAll('button.audio-snippet');
        createdSpeakerButton[speakerURLIndexCount].innerText = firstJSONData[speakerURLIndexCount].speaker_name;
        // for testing purposes
        // console.log(createdSpeakerButton[speakerURLIndexCount]);
        createdSpeakerButton[speakerURLIndexCount].addEventListener('click', function() {
          // for testing purposes
          // console.log('A button at index ' + speakerURLIndexCount + ' was clicked.');

          // wait. if it's working here, I might be able to get the audio in here in time for the demo and refactor later?
          var audio = new Audio(firstJSONData[speakerURLIndexCount].recording_url);
          audio.type = 'audio/m4a';
          audio.play();

          // what i want to do is grab the JSON and make an array based on the speaker_url property. with that, I want to grab the things associated with it – the speaker name, namely. i also want to keep the position of the speaker_urls as they are.
        });
      }
    }
  }

  // send the request!
  xhttp.send();
}