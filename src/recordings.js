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
export function displaySpeakerList(wordform) {
  // purely for testing purposes
  // console.log('Hey, we\'re clicked and working!');
  
  // get the value of the wordform from the page
  wordform = document.getElementById('data:head').value;

  const recordingsList = document.querySelector('.recordings');
  const BASE_URL = 'http://sapir.artsrn.ualberta.ca/validation/recording/_search/' + `${wordform}`;

  // setting up the JSON request
  let xhttp = new XMLHttpRequest();
  xhttp.open('GET', BASE_URL, true);
  xhttp.responseType = 'json';
  xhttp.send();

  // receiving request information from SAPIR
  xhttp.onload = function() {
    let returnedData = xhttp.response;
    // a test,,,as a treat:
    console.log(returnedData);
  }
    
  // build out JS for displaying speaker list

  // tooltip pops up (or div to start)

  // get the list of speaker URLs from JSON list

  // click the list to be able to hear the different speakers
}