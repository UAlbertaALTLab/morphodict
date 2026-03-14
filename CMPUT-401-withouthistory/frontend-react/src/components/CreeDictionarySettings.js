/*
Name   : CreeDictionarySettings
Inputs : Props () None Allowed

Goal   : Allows the user to chaneg the settings of the app
*/

import { ListGroup, Form } from "react-bootstrap";
import "../../node_modules/bootstrap/dist/css/bootstrap.min.css";
import "react-bootstrap";
import Settings from "../HelperClasses/SettingClass";

function CreeDictionarySettings(props) {
  let changeSettingsMain = (e) => {
    switch (e.target.id) {
      case "plain-engl":
        settings.plainEngl = true;
        settings.lingLabel = false;
        settings.niyaLabel = false;
        break;
      case "ling":
        settings.plainEngl = false;
        settings.lingLabel = true;
        settings.niyaLabel = false;
        break;
      case "nêhiyaw":
        settings.plainEngl = false;
        settings.lingLabel = false;
        settings.niyaLabel = true;
        break;
      default:
        break;
    }

    window.localStorage.setItem("settings", JSON.stringify(settings));
  };

  let changeSettingsEmoji = (e) => {
    settings.active_emoti = e.target.id;
    window.localStorage.setItem("settings", JSON.stringify(settings));
  };

  let changeSettingsDicts = (e) => {
    switch (e.target.id) {
      case "MD-DIC":
        settings.md_source = true;
        settings.cw_source = false;
        settings.both_sources = false;
        break;
      case "CW-DIC":
        settings.md_source = false;
        settings.cw_source = true;
        settings.both_sources = false;
        break;
      case "ALL-DIC":
        settings.md_source = false;
        settings.cw_source = false;
        settings.both_sources = true;
        break;
      default:
        break;
    }
    window.localStorage.setItem("settings", JSON.stringify(settings));
  };

  let changeSettingsAudio = (e) => {
    switch (e.target.id) {
      case "audio-yes":
        settings.showAudio = true;
        break;
      case "audio-no":
        settings.showAudio = false;
        break;
      default:
        break;
    }

    window.localStorage.setItem("settings", JSON.stringify(settings));
  };

  let localStorage = window.localStorage;

  let settings = localStorage.getItem("settings");
  if (!settings) {
    settings = new Settings();
    localStorage.setItem("settings", JSON.stringify(settings));
  }
  settings = JSON.parse(localStorage.getItem("settings"));

  return (
    <div className="container bg-white">
      <h1>Settings</h1>

      <h2>Paradigm labels</h2>
      <p className="font-weight-light">
        These are the labels that appear on the <b>paradigm table</b> to label
        features like person, tense, plurals, etc.
      </p>

      <ListGroup variant="flush">
        <ListGroup.Item>
          <Form.Check
            type={"radio"}
            id={"plain-engl"}
            name="engl_type"
            label="Plain English labels"
            defaultChecked={settings.plainEngl ? true : false}
            value={settings.plainEngl}
            onChange={changeSettingsMain}
          />
          <p className="font-weight-light">
            Examples: I, you (one), s/he; something is happening now, something
            happened earlier
          </p>
        </ListGroup.Item>

        <ListGroup.Item>
          <Form.Check
            type={"radio"}
            id={"ling"}
            name="engl_type"
            label="Linguistic labels"
            defaultChecked={settings.lingLabel ? true : false}
            value={settings.lingLabel}
            onChange={changeSettingsMain}
          />
          <p className="font-weight-light">
            Examples: 1s, 2s, 3s; Present, Past
          </p>
        </ListGroup.Item>
        <ListGroup.Item>
          <Form.Check
            type={"radio"}
            id={"nêhiyaw"}
            name="engl_type"
            label="Nêhiyawêwin labels"
            defaultChecked={settings.niyaLabel ? true : false}
            value={settings.niyaLabel}
            onChange={changeSettingsMain}
          />
          <p className="font-weight-light">
            Examples: niya, kiya, wiya; ê-ispayik anohc/mêkwâc/mâna, ê-ispayik
            kwayâc
          </p>
        </ListGroup.Item>
      </ListGroup>

      <h2>Emoji for animate nouns (awa words)</h2>
      <p className="font-weight-light">
        Choose the emoji that will represent all awa words.
      </p>

      <ListGroup variant="flush">
        <ListGroup.Item>
          <Form.Check
            type={"radio"}
            id={"🧑🏽"}
            name="emoji"
            label="🧑🏽"
            defaultChecked={settings.active_emoti === "🧑🏽" ? true : false}
            onChange={changeSettingsEmoji}
          />
        </ListGroup.Item>
        <ListGroup.Item>
          <Form.Check
            type={"radio"}
            id={"👵🏽"}
            name="emoji"
            label="👵🏽"
            defaultChecked={settings.active_emoti === "👵🏽" ? true : false}
            onChange={changeSettingsEmoji}
          />
        </ListGroup.Item>
        <ListGroup.Item>
          <Form.Check
            type={"radio"}
            id={"👴🏽"}
            name="emoji"
            label="👴🏽"
            defaultChecked={settings.active_emoti === "👴🏽" ? true : false}
            onChange={changeSettingsEmoji}
          />
        </ListGroup.Item>

        <ListGroup.Item>
          <Form.Check
            type={"radio"}
            id={"🐺"}
            name="emoji"
            label="🐺"
            defaultChecked={settings.active_emoti === "🐺" ? true : false}
            onChange={changeSettingsEmoji}
          />
        </ListGroup.Item>
        <ListGroup.Item>
          <Form.Check
            type={"radio"}
            id={"🐻"}
            name="emoji"
            label="🐻"
            defaultChecked={settings.active_emoti === "🐻" ? true : false}
            onChange={changeSettingsEmoji}
          />
        </ListGroup.Item>
        <ListGroup.Item>
          <Form.Check
            type={"radio"}
            id={"🍞"}
            name="emoji"
            label="🍞"
            defaultChecked={settings.active_emoti === "🍞" ? true : false}
            onChange={changeSettingsEmoji}
          />
        </ListGroup.Item>
        <ListGroup.Item>
          <Form.Check
            type={"radio"}
            id={"🌟"}
            name="emoji"
            label="🌟"
            defaultChecked={settings.active_emoti === "🌟" ? true : false}
            onChange={changeSettingsEmoji}
          />
        </ListGroup.Item>
      </ListGroup>

      <h2>Select Dictionary Source</h2>
      <p className="font-weight-light">
        Select one of the following options to chose which entries are displayed
        in the search results
      </p>

      <ListGroup variant="flush">
        <ListGroup.Item>
          <Form.Check
            type={"radio"}
            id={"CW-DIC"}
            name="dict-sources"
            label="CW"
            defaultChecked={settings.cw_source ? true : false}
            value={settings.cw_source}
            onChange={changeSettingsDicts}
          />
          <p>
            Show entries from the Cree: Words dictionary. Wolvengrey, Arok,
            editor. Cree: Words. Regina, University of Regina Press, 2001
          </p>
        </ListGroup.Item>
        <ListGroup.Item>
          <Form.Check
            type={"radio"}
            id={"MD-DIC"}
            name="dict-sources"
            label="MD"
            defaultChecked={settings.md_sources ? true : false}
            value={settings.md_sources}
            onChange={changeSettingsDicts}
          />
          <p>
            Show entries from the Maskwacîs Dictionary. Maskwacîs Dictionary.
            Maskwacîs, Maskwachees Cultural College, 1998.
          </p>
        </ListGroup.Item>
        <ListGroup.Item>
          <Form.Check
            type={"radio"}
            id={"ALL-DIC"}
            name="dict-sources"
            label="CW-MD"
            defaultChecked={settings.both_sources ? true : false}
            value={settings.both_sources}
            onChange={changeSettingsDicts}
          />
          Show entries from CW and MD (default)
        </ListGroup.Item>
      </ListGroup>

      <h2>Show Paradigm Audio</h2>
      <p className="font-weight-light">
        When available, paradigm audio will be displayed and played in paradigms
      </p>

      <ListGroup variant="flush">
        <ListGroup.Item>
          <Form.Check
            type={"radio"}
            id={"audio-yes"}
            name="audio-select"
            label="Yes"
            defaultChecked={settings.showAudio ? true : false}
            value={settings.showAudio}
            onChange={changeSettingsAudio}
          />
          <p>I would like to see audio in paradigm layouts</p>
        </ListGroup.Item>
        <ListGroup.Item>
          <Form.Check
            type={"radio"}
            id={"audio-no"}
            name="audio-select"
            label="No"
            defaultChecked={settings.showAudio ? false : true}
            value={!settings.showAudio}
            onChange={changeSettingsAudio}
          />
          <p>I do not want to see audio in paradigm layouts</p>
        </ListGroup.Item>
      </ListGroup>
    </div>
  );
}

export default CreeDictionarySettings;
