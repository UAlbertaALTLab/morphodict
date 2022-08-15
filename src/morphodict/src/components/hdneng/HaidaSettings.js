import Settings from "../../HelperClasses/SettingClass";
import {Form, ListGroup} from "react-bootstrap";

function HaidaSettings(props) {
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
                        label="X̲aad Kíl labels"
                        defaultChecked={settings.niyaLabel ? true : false}
                        value={settings.niyaLabel}
                        onChange={changeSettingsMain}
                    />
                </ListGroup.Item>
            </ListGroup>
        </div>
    );
}

export default HaidaSettings;
