import Settings from "../../HelperClasses/SettingClass";
import {Form, ListGroup} from "react-bootstrap";

function WoodsCreeSettings(props) {
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

    let changeSettingsEmoji = (e) => {

        settings = JSON.parse(localStorage.getItem("settings"));
        settings.active_emoti = e.target.id;
        window.localStorage.setItem("settings", JSON.stringify(settings));
    };

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
                        label="nîhithawîwin labels"
                        defaultChecked={settings.niyaLabel ? true : false}
                        value={settings.niyaLabel}
                        onChange={changeSettingsMain}
                    />
                    <p className="font-weight-light">
                        Examples: niyu, kiyu, wiyu; ê-ispayik anohc/mêkwâc/mâna, ê-ispayik kwayâc
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
        </div>
    );
}

export default WoodsCreeSettings;
