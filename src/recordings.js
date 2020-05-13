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

export function displaySpeakerList() {
  // purely for testing purposes
  console.log('Hey, we\'re clicked and working!');
    
  // build out JS for displaying speaker list

  // tooltip pops up

  // get the list of speaker URLs from JSON list

  // click the list to be able to hear the different speakers
}