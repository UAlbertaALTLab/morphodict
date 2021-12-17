export async function loadParadigmAudio() {
    for (let button of document.querySelectorAll("[data-cy='play-recording-paradigm']")) {
        button.addEventListener("click", async (e) => {
            const recordingURL = e.target.dataset.recUrl;

            const recording = new Audio(recordingURL);
            recording.type = "audio/mp4";
            recording.preload = "none";
            try {
                await recording.play();
              } catch (err) {
                console.log('Failed to play...' + err);
              }
        })
    }
}
