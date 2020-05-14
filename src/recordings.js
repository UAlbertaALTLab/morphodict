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
  // purely for testing purposes
  // console.log('Hey, we\'re clicked and working!');
  
  // get the value of the wordform from the page
  wordform = document.getElementById('data:head').value;

  const BASE_URL = 'http://sapir.artsrn.ualberta.ca/validation/recording/_search/' + `${wordform}`;

  // setting up the JSON request
  let xhttp = new XMLHttpRequest();
  xhttp.open('GET', BASE_URL, true);

  // sending + receiving request information from SAPIR
  xhttp.onload = function() {
    let returnedData = JSON.parse(this.response);
    
    // display individual speaker's name
    function displaySpeakerList(jsonObj) {
      const recordingsList = document.querySelector('.recordings');
      let speakerListIndex = 0;
    
      while (speakerListIndex < returnedData.length) {
        const individualSpeaker = document.createElement('li');

        // the value of the list item's text content is actually a loop through the names of the speakers for the particular wordform
        individualSpeaker.textContent = jsonObj[speakerListIndex].speaker_name;
        
        // grab data and put it into the Paradigms' page
        recordingsList.appendChild(individualSpeaker);
        speakerListIndex++;
      }
    }
    displaySpeakerList(returnedData);
  }

  xhttp.send();

  // get the list of speaker URLs from JSON list

  // click the list to be able to hear the different speakers
}