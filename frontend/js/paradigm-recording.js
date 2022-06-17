export function loadParadigmAudio() {
  for (let button of document.querySelectorAll(
    "[data-cy='play-recording-paradigm']"
  )) {
    button.addEventListener("click", (e) => {
      const inflection = e.target.dataset.inflection;
      console.log(e.target);
      console.log(inflection);

      const audio = document.getElementById(
        `recording-url-paradigm-${inflection}`
      );
      audio.play();
    });
  }
}
