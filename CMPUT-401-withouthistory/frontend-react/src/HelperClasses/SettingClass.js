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
    this.active_emoti = "🧑🏽";

    // dict sources

    this.cw_source = false;
    this.md_source = false;
    this.both_sources = true;

    // word_types
    this.latn = true; //angle hat
    this.latn_x_macron = false; // flat_head
    this.syllabics = false;

    this.currentType = "Latn";

    // Audio Options
    this.showAudio = false;
  }
}

export default Settings;
