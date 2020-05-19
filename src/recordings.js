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
 * Render multiple speakers for the user to click + hear
 *
 * @param wordform {string} – the term being defined
 * 
 */
export function getSpeakerList(wordform) {  
  // get the value of the wordform from the page
  wordform = document.getElementById('data:head').value;
  const BASE_URL = 'http://sapir.artsrn.ualberta.ca/validation/recording/_search/' + `${wordform}`;

  // setting up the JSON request
  let xhttp = new XMLHttpRequest();
  xhttp.open('GET', BASE_URL, true);

  // receiving request information from SAPIR
  xhttp.onload = function() {
    let returnedData = JSON.parse(this.response);
    
    // display individual speaker's name
    function displaySpeakerList(firstJSONData) {
      const recordingsHeading = document.querySelector('.definition__recordings');
      recordingsHeading.insertAdjacentHTML('afterbegin', '<h3 class="explainer">Tap the names below to hear the word said by various speakers.</h3>');
      const recordingsList = document.querySelector('.recordings');
      let speakerListIndex = 0;

      // TODO: the check for if the list items exist already should go here (and probably encapsulate the bulk of the while loop.
    
      while (speakerListIndex < returnedData.length) {
        const individualSpeaker = document.createElement('li');

        // the value of each list item is actually a loop through the names of the speakers for the particular wordform
        individualSpeaker.innerHTML = '<a class="audio-snippet">' + firstJSONData[speakerListIndex].speaker_name + '</a>';
        
        // grab data and 'load' it on the paradigm page
        recordingsList.appendChild(individualSpeaker);
        speakerListIndex++;
      }
      // after creation of the speakers (as list items), we select for them...
      const speakerNodeList = document.querySelectorAll('.audio-snippet');
      
      // ...and place an event listener on every item in the nodelist – the speaker names – so we can have the playback occur via the playRecording() function.
      for (let index = 0; index < speakerNodeList.length; index++) {
        speakerNodeList[index].addEventListener('click', playRecording);
      }
    }
    displaySpeakerList(returnedData);
  }

  // send the request!
  xhttp.send();
}


/**
 * Allow the clicking of users to hear wordforms in different styles
 *
 * @param wordform {string} – the term being defined
 * @param speakerName {string} – the name of the speaker
 */
export function playRecording(speakerName, wordform) {
  wordform = document.getElementById('data:head').value;
  speakerName = speakerName.path[0].innerHTML; // there's probably a much more elegant way to get this but I'm blanking at present 🤔

  // - the URL for the JSON data (will be used in a XMLHttpRequest)
  const NEW_BASE_URL = 'http://sapir.artsrn.ualberta.ca/validation/recording/_search/' + `${wordform}`;

  // set up the request
  let secondRequest = new XMLHttpRequest();
  secondRequest.open('GET', NEW_BASE_URL, true);

  // actually make the request
  secondRequest.onload = function() {
    let secondJSONData = JSON.parse(this.response);
    // console.log(secondJSONData);
    console.log('Just for clarification, the person who said this was ' + speakerName);

    // We need to access the URL of the speaker (clicked) and get some audio output

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

// a loop for looping through the speaker items (nodelist) and adding something to their classlist
// for (let i = 0; i < speakerNodeList.length; i++) {
//   speakerNodeList[i].addEventListener('click', function() {
//       speakerNodeList[i].classList.add('yerr');
//   });
// }