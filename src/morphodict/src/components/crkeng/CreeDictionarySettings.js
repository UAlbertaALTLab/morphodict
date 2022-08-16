/*
Name   : CreeDictionarySettings
Inputs : Props () None Allowed

Goal   : Allows the user to chaneg the settings of the app
*/

import {ListGroup, Form} from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import "react-bootstrap";
import Settings from "../../HelperClasses/SettingClass";

function CreeDictionarySettings(props) {
    let localStorage = window.localStorage;

    let settings = localStorage.getItem("settings");
    if (!settings) {
        settings = new Settings();
        localStorage.setItem("settings", JSON.stringify(settings));
    }

    settings = JSON.parse(localStorage.getItem("settings"));

    let changeSettingsMain = (e) => {

        settings = JSON.parse(localStorage.getItem("settings"));
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

        settings = JSON.parse(localStorage.getItem("settings"));
        settings.active_emoti = e.target.id;
        window.localStorage.setItem("settings", JSON.stringify(settings));
    };

    let changeSettingsDicts = (e) => {

        settings = JSON.parse(localStorage.getItem("settings"));
        switch (e.target.id) {
            case "MD-DIC":
                settings.md_source = true;
                settings.cw_source = false;
                settings.aecd_source = false;
                settings.all_sources = false;
                break;
            case "CW-DIC":
                settings.md_source = false;
                settings.cw_source = true;
                settings.aecd_source = false;
                settings.all_sources = false;
                break;
            case "AECD-DIC":
                settings.md_source = false;
                settings.cw_source = false;
                settings.aecd_source = true;
                settings.all_sources = false;
                break;
            case "ALL-DIC":
                settings.md_source = false;
                settings.cw_source = false;
                settings.aecd_source = false;
                settings.all_sources = true;
                break;
            default:
                break;
        }
        window.localStorage.setItem("settings", JSON.stringify(settings));
    };

    let changeSettingsAudio = (e) => {
        settings = JSON.parse(localStorage.getItem("settings"));
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

    let changeSettingsAudioSource = (e) => {
        settings = JSON.parse(localStorage.getItem("settings"));
        switch (e.target.id) {
            case "MD-AUDIO":
                settings.md_audio = true;
                settings.mos_audio = false;
                settings.both_audio = false;
                break;
            case "MOS-AUDIO":
                settings.md_audio = false;
                settings.mos_audio = true;
                settings.both_audio = false;
                break;
            case "ALL-AUDIO":
                settings.md_audio = false;
                settings.mos_audio = false;
                settings.both_audio = true;
                break;
            default:
                break;
        }

        window.localStorage.setItem("settings", JSON.stringify(settings));
    }

    let changeSettingsMorphemes = (e) => {
        settings = JSON.parse(localStorage.getItem("settings"));
         switch (e.target.id) {
            case "MORPH-EVERYWHERE":
                settings.morphemes_everywhere = true;
                settings.morphemes_headers = false;
                settings.morphemes_paradigms = false;
                settings.morphemes_nowhere = false;
                break;
            case "MORPH-HEADERS":
                settings.morphemes_everywhere = false;
                settings.morphemes_headers = true;
                settings.morphemes_paradigms = false;
                settings.morphemes_nowhere = false;
                break;
            case "MORPH-PARADIGMS":
                settings.morphemes_everywhere = false;
                settings.morphemes_headers = false;
                settings.morphemes_paradigms = true;
                settings.morphemes_nowhere = false;
                break;
            case "MORPH-NOWHERE":
                settings.morphemes_everywhere = false;
                settings.morphemes_headers = false;
                settings.morphemes_paradigms = false;
                settings.morphemes_nowhere = true;
                break;
            default:
                break;
        }

        window.localStorage.setItem("settings", JSON.stringify(settings));
    }

    let changeSettingsIc = (e) => {
        settings = JSON.parse(localStorage.getItem("settings"));
        switch (e.target.id) {
            case "IC-YES":
                settings.showIC = true;
                break;
            case "IC-NO":
                settings.showIC = false;
                break;
            default:
                break;
        }

        window.localStorage.setItem("settings", JSON.stringify(settings));
    }

    let changeSettingsShowEmoji = (e) => {
        settings = JSON.parse(localStorage.getItem("settings"));
        switch (e.target.id) {
            case "SHOW-EMOJI-YES":
                settings.showEmoji = true;
                break;
            case "SHOW-EMOJI-NO":
                settings.showEmoji = false;
                break;
            default:
                break;
        }

        window.localStorage.setItem("settings", JSON.stringify(settings));
    }

    let changeSettingsSynthAudio = (e) => {
        settings = JSON.parse(localStorage.getItem("settings"));
        switch (e.target.id) {
            case "SYNTH-YES":
                settings.synthAudio = true;
                break;
            case "SYNTH-NO":
                settings.synthAudio = false;
                break;
            default:
                break;
        }

        window.localStorage.setItem("settings", JSON.stringify(settings));
    }

    let changeSettingsSynthAudioParadigm = (e) => {
        settings = JSON.parse(localStorage.getItem("settings"));
        switch (e.target.id) {
            case "SYNTH-YES-PARA":
                settings.synthAudioParadigm = true;
                break;
            case "SYNTH-NO-PARA":
                settings.synthAudioParadigm = false;
                break;
            default:
                break;
        }

        window.localStorage.setItem("settings", JSON.stringify(settings));
    }

    let changeSettingsEspt = (e) => {
        settings = JSON.parse(localStorage.getItem("settings"));
        switch (e.target.id) {
            case "ESPT-YES":
                settings.espt = true;
                break;
            case "ESPT-NO":
                settings.espt = false;
                break;
            default:
                break;
        }

        window.localStorage.setItem("settings", JSON.stringify(settings));
    }

    let changeSettingsAuto = (e) => {
        settings = JSON.parse(localStorage.getItem("settings"));
        switch (e.target.id) {
            case "AUTO-YES":
                settings.autoTranslate = true;
                break;
            case "AUTO-NO":
                settings.autoTranslate = false;
                break;
            default:
                break;
        }

        window.localStorage.setItem("settings", JSON.stringify(settings));
    }

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
                        label="nêhiyawêwin labels"
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

            <h2>Show Morpheme Boundaries</h2>
            <p className="font-weight-light">
                Where would you like morpheme boundaries to be shown?</p>

            <ListGroup variant="flush">
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"MORPH-EVERYWHERE"}
                        name="morphemes"
                        label="Everywhere"
                        defaultChecked={settings.morphemes_everywhere ? true : false}
                        value={settings.morphemes_everywhere}
                        onChange={changeSettingsMorphemes}
                    />
                    <p>
                        Show morpheme boundaries everywhere
                    </p>
                </ListGroup.Item>
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"MORPH-HEADERS"}
                        name="morphemes"
                        label="Headers"
                        defaultChecked={settings.morphemes_headers ? true : false}
                        value={settings.morphemes_headers}
                        onChange={changeSettingsMorphemes}
                    />
                    <p>
                        Show morpheme boundaries in entry headers only
                    </p>
                </ListGroup.Item>
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"MORPH-PARADIGMS"}
                        name="morphemes"
                        label="Paradigms"
                        defaultChecked={settings.morphemes_paradigms ? true : false}
                        value={settings.morphemes_paradigms}
                        onChange={changeSettingsMorphemes}
                    />
                    <p>
                        Show morpheme boundaries in the paradigms
                    </p>
                </ListGroup.Item>
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"MORPH-NOWHERE"}
                        name="morphemes"
                        label="Nowhere"
                        defaultChecked={settings.morphemes_nowhere ? true : false}
                        value={settings.morphemes_nowhere}
                        onChange={changeSettingsMorphemes}
                    />
                    <p>
                        Don't show morpheme boundaries anywhere
                    </p>
                </ListGroup.Item>
            </ListGroup>

            <h2>Show Inflectional Category</h2>
            <p className="font-weight-light">
                Would you like to see the inflectional category?</p>

            <ListGroup variant="flush">
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"IC-YES"}
                        name="ic"
                        label="Yes"
                        defaultChecked={settings.showIC ? true : false}
                        value={settings.showIC}
                        onChange={changeSettingsIc}
                    />
                    <p>
                        I want to see the inflectional category with every entry
                    </p>
                </ListGroup.Item>
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"IC-NO"}
                        name="ic"
                        label="No"
                        defaultChecked={settings.ShowIC ? false : true}
                        value={settings.ShowIC}
                        onChange={changeSettingsIc}
                    />
                    <p>
                        I don't want to see the inflectional category with entries
                    </p>
                </ListGroup.Item>
            </ListGroup>

            <h2>Show Emojis</h2>
            <p className="font-weight-light">
                Would you like to see the emojis?</p>

            <ListGroup variant="flush">
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"SHOW-EMOJI-YES"}
                        name="show-emoji"
                        label="Yes"
                        defaultChecked={settings.showEmoji ? true : false}
                        value={settings.showEmoji}
                        onChange={changeSettingsShowEmoji}
                    />
                    <p>
                        I want to see emojis
                    </p>
                </ListGroup.Item>
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"SHOW-EMOJI-NO"}
                        name="show-emoji"
                        label="No"
                        defaultChecked={settings.showEmoji ? false : true}
                        value={settings.showEmoji}
                        onChange={changeSettingsShowEmoji}
                    />
                    <p>
                        I do not want to see emojis
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
                        defaultChecked={settings.md_source ? true : false}
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
                        id={"AECD-DIC"}
                        name="dict-sources"
                        label="AECD"
                        defaultChecked={settings.aecd_source ? true : false}
                        value={settings.aecd_sources}
                        onChange={changeSettingsDicts}
                    />
                    <p>
                        Show entries from the Alberta Elders' Cree Dictionary/alberta ohci kehtehayak nehiyaw otwestamâkewasinahikan compiled by Nancy LeClaire and George Cardinal, edited by Earle H. Waugh. Edmonton: University of Alberta Press, 2002.
                    </p>
                </ListGroup.Item>
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"ALL-DIC"}
                        name="dict-sources"
                        label="All"
                        defaultChecked={settings.all_sources ? true : false}
                        value={settings.all_sources}
                        onChange={changeSettingsDicts}
                    />
                    Show entries from all sources (default)
                </ListGroup.Item>
            </ListGroup>

            <h2>Select Audio Source</h2>
            <p className="font-weight-light">
                Select one of the following options to chose which audio sources you'd like to hear
            </p>

            <ListGroup variant="flush">
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"MD-AUDIO"}
                        name="audio-sources"
                        label="Maskwacîs"
                        defaultChecked={settings.md_audio ? true : false}
                        value={settings.md_audio}
                        onChange={changeSettingsAudioSource}
                    />
                    <p>
                        Show recordings from Maskwacîs.
                    </p>
                </ListGroup.Item>
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"MOS-AUDIO"}
                        name="audio-sources"
                        label="mōswacīhk"
                        defaultChecked={settings.mos_audio ? true : false}
                        value={settings.mos_audio}
                        onChange={changeSettingsAudioSource}
                    />
                    <p>
                        Show recordings from mōswacīhk.
                    </p>
                </ListGroup.Item>
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"ALL-AUDIO"}
                        name="audio-sources"
                        label="Both"
                        defaultChecked={settings.both_audio ? true : false}
                        value={settings.both_audio}
                        onChange={changeSettingsAudioSource}
                    />
                    Show recordings from Maskwacîs and mōswacīhk
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

            <h2>Show Synthesized Audio</h2>
            <p className="font-weight-light">
                Synthesized audio is generated by a computer model. It is fairly accurate, but not as precise or natural
                as a human speaker. This setting applies to all speech except the paradigm layouts.
            </p>

            <ListGroup variant="flush">
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"SYNTH-YES"}
                        name="synth-audio"
                        label="Yes"
                        defaultChecked={settings.synthAudio ? true : false}
                        value={settings.synthAudio}
                        onChange={changeSettingsSynthAudio}
                    />
                    <p>
                        Show synthesized recordings
                    </p>
                </ListGroup.Item>
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"SYNTH-NO"}
                        name="synth-audio"
                        label="No"
                        defaultChecked={settings.synthAudio ? false : true}
                        value={settings.synthAudio}
                        onChange={changeSettingsSynthAudio}
                    />
                    <p>
                        Don't show synthesized recordings
                    </p>
                </ListGroup.Item>
            </ListGroup>

            <h2>Show Synthesized Audio in Paradigms</h2>
            <p className="font-weight-light">
                Synthesized audio is generated by a computer model. It is fairly accurate, but not as precise or natural
                as a human speaker. This setting applies to the Paradigm Layouts specifically. <i>Note: this setting
                only applies if "Show Paradigm Audio" is set to "yes"</i></p>

            <ListGroup variant="flush">
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"SYNTH-YES-PARA"}
                        name="synth-audio-paradigm"
                        label="Yes"
                        defaultChecked={settings.synthAudioParadigm ? true : false}
                        value={settings.synthAudioParadigm}
                        onChange={changeSettingsSynthAudioParadigm}
                    />
                    <p>
                        Show synthesized recordings in the paradigms
                    </p>
                </ListGroup.Item>
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"SYNTH-NO-PARA"}
                        name="synth-audio-paradigm"
                        label="No"
                        defaultChecked={settings.synthAudioParadigm ? false : true}
                        value={settings.synthAudioParadigm}
                        onChange={changeSettingsSynthAudioParadigm}
                    />
                    <p>
                        Don't show synthesized recordings in the paradigms
                    </p>
                </ListGroup.Item>
            </ListGroup>

            <h2>Automatically translate English phrases into Cree word-forms</h2>

            <ListGroup variant="flush">
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"ESPT-YES"}
                        name="espt"
                        label="Yes"
                        defaultChecked={settings.espt ? true : false}
                        value={settings.espt}
                        onChange={changeSettingsEspt}
                    />
                    <p>
                        Generate Cree word-forms matching simple English verb or noun phrases
                    </p>
                </ListGroup.Item>
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"ESPT-NO"}
                        name="espt"
                        label="No"
                        defaultChecked={settings.espt ? false : true}
                        value={settings.espt}
                        onChange={changeSettingsEspt}
                    />
                    <p>
                        Only show dictionary entry headwords as they are
                    </p>
                </ListGroup.Item>
            </ListGroup>

            <h2>Automatically translate Cree word-forms into English phrases</h2>

            <ListGroup variant="flush">
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"AUTO-YES"}
                        name="auto"
                        label="Yes"
                        defaultChecked={settings.autoTranslate ? true : false}
                        value={settings.autoTranslate}
                        onChange={changeSettingsAuto}
                    />
                    <p>
                        Generate English definitions matching core Cree word-forms
                    </p>
                </ListGroup.Item>
                <ListGroup.Item>
                    <Form.Check
                        type={"radio"}
                        id={"AUTO-NO"}
                        name="auto"
                        label="No"
                        defaultChecked={settings.autoTranslate ? false : true}
                        value={settings.autoTranslate}
                        onChange={changeSettingsAuto}
                    />
                    <p>
                        Only show dictionary definitions as they are
                    </p>
                </ListGroup.Item>
            </ListGroup>
        </div>
    );
}

export default CreeDictionarySettings;
