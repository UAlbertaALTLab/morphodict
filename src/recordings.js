// TODO: pull out BASE_URL and declare it as a const to be used by fetchRecordings, getSpeakerList, etc...AFTER THE TEST PASSES!!!
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
      let speakerListIndex = 0;
      
      
      while (speakerListIndex < numberOfRecordings) {
        let individualSpeaker = document.createElement('li');
        // dynamically alter the classlist of the newly created element to fit BEM methodology
        individualSpeaker.classList.add('recordings-list__item');
        
        
        let speakerButton = document.createElement('button');
        speakerButton.classList.add('audio-snippet');

        speakerButton.innerText = 'Name associated with URL at index ' + speakerListIndex;

        individualSpeaker.appendChild(speakerButton);

        // individualSpeaker.innerText = speakerButton;
        recordingsList.appendChild(individualSpeaker);
        speakerListIndex++;
      }

      // while (speakerListIndex < numberOfRecordings) {
      //   const individualSpeaker = document.createElement('li');

      //   // TODO: previously, the assumption was: one speaker has one URL associated with them and we'll use the speaker name to be our reference point for building our list. NOW, this assumption breaks when one speaker has multiple URLs associated with them. instead, we'll go with the URLs as the reference point: one URL has one speaker associated with it (so as a rough off the top example, "for every URL, give us the speaker name associated with it").
    
      //   // the value of each list item is actually a loop through the names of the speakers for the particular wordform
      //   individualSpeaker.innerHTML = '<button class="audio-snippet">' + firstJSONData[speakerListIndex].speaker_name + '</button>';
      //   // TODO: document.createElement('button')
      //   // TODO: add class
      //   // TODO: innerText
      //   // TODO: registerEventListener('click', {
      //   // TODO: use: firstJSONData[speakerListIndex].recording_url
      //   // })
      //   //var audio = new Audio(retrievedSpeakerURL);
      //   //  audio.type = 'audio/m4a'; // not fully sure if this is absolutely needed: it works without it, but maybe some browsers will require it!
      //   // audio.play();
            
      //   // grab data and 'load' it on the paradigm page
      //   recordingsList.appendChild(individualSpeaker);
      //   speakerListIndex++;
      // }
      
      // after creation of the speakers (as list items), we select for them...
      // const speakerNodeList = document.querySelectorAll('.audio-snippet');
      
      // ...and place an event listener on every item in the nodelist – the speaker names – so we can have the playback occur via the playRecording() function.
      // for (let index = 0; index < speakerNodeList.length; index++) {
      //   speakerNodeList[index].addEventListener('click', playRecording);
      // }
    }
  }

  // send the request!
  xhttp.send();
}


/**
 * Allow the clicking of users to hear wordforms in different styles
 *
 * @param wordform {string} – the term being defined
 * @param speakerName {MouseEvent} – the name of the speaker
 */
export function playRecording(speakerName, wordform) {
  wordform = document.getElementById('data:head').value;
  speakerName = speakerName.target
  
  .path[0].innerHTML; // there's probably a much more elegant way to get this but I'm blanking at present 🤔

  // - the URL for the JSON data (will be used in a XMLHttpRequest)
  const NEW_BASE_URL = 'http://sapir.artsrn.ualberta.ca/validation/recording/_search/' + `${wordform}`;

  // set up the request
  let secondRequest = new XMLHttpRequest();
  secondRequest.open('GET', NEW_BASE_URL, true);

  // actually make the request
  secondRequest.onload = function() {
    let secondJSONData = JSON.parse(this.response);

    // We need to access the URL of the speaker (clicked) and get some audio output:
    // this reaches into the JSON and grabs the JSON of the person clicked (assuming there are NOT repeats)
    let retrievedJSONData = secondJSONData.filter(function(testvar) {
      return testvar.speaker_name == speakerName;
    });

    // grab the URL property of the JSON object (for the selected speaker) and put it into a variable for manipulation
    let retrievedSpeakerURL = (retrievedJSONData[0].recording_url);

    // there's probably an argument to be made that this audio stuff should be placed in its own function...?
    var audio = new Audio(retrievedSpeakerURL);
    audio.type = 'audio/m4a'; // not fully sure if this is absolutely needed: it works without it, but maybe some browsers will require it!
    audio.play();
  }

  // send the request!!
  secondRequest.send();
}