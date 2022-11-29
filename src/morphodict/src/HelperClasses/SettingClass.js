/*
Name   : SettingClass
Inputs : None
       
Goal   : goal of this file is to maintain the current
         setting s of the page so we don't need to store cookies.  
       
Testing: 
        (1) N/A 

TODO: Perhaps move functionality here instead of keeping them 
      in their own comps. Will improve readability. 
*/

class Settings {
  constructor() {
    // Settings main
    this.plainEngl = true;
    this.lingLabel = false;
    this.niyaLabel = false;

    // Options: English, Linguistic (long), Linguistic (short), source language
    this.label = "ENGLISH";

    // Settings emoti
    this.emojis = {
      man: "🧑🏽",
      gamma: "👵🏽",
      gapa: "👴🏽",
      wolf: "🐺",
      bear: "🐻",
      bread: "🍞",
      star: "🌟",
    };
    this.active_emoji = "🧑🏽";

    // dict sources

    this.cw_source = false;
    this.md_source = false;
    this.aecd_source = false;
    this.all_sources = true;

    // word_types
    this.latn = true; //angle hat
    this.latn_x_macron = false; // flat_head
    this.syllabics = false;

    this.currentType = "Latn";

    // Audio Options
    this.showAudio = false;

    // Show synthesized audio
    this.synthAudio = false;

    // Show synth audio in paradigms
    this.synthAudioParadigm = false;

    // Turns ESPT on?
    this.espt = false;

    // Turn AUTO on?
    this.autoTranslate = false;

    // Show emojis?
    this.showEmoji = true;

    // Show the inflectional category?
    this.showIC = true;

    // Where to show morpheme boundaries
    this.morphemes_everywhere = false;
    this.morphemes_headers = false;
    this.morphemes_paradigms = false;
    this.morphemes_nowhere = true;

    // audio sources
    this.md_audio = false;
    this.mos_audio = false;
    this.both_audio = true;
  }
}

export default Settings;
