function SingleColumnRow(props) {
    const cell_list = props.cells;
    const labelType = props.labelType;
    const labels = props.labels;
    const counter = props.counter;
    const type = props.type;
    const showAudio = JSON.parse(window.localStorage.getItem("settings"))["showAudio"];
    let settings = JSON.parse(window.localStorage.getItem("settings"));
    console.log("Label type:", labelType);
    console.log(labels)


    const cell_layouts = cell_list.map((cell, index) => {
        if (cell.is_label) {
            const class_name = "paradigm-label paradigm-label--" + cell.label_for;
            if (!labels[cell.label.join("+")]) {
                return <></>
            }
            return (
                <th
                    scope={cell.label_for}
                    rowSpan={1}
                    className={class_name}
                    key={counter.toString() + '-' + index.toString()}
                >
                    {labels[cell.label.join("+")][labelType]}
                </th>
            );
        } else if (cell.is_missing) {
            return (
                <td className="paradigm-cell paradigm-cell--missing" key={index}>
                    &mdash;
                </td>
            );
        } else if (cell.is_empty) {
            return (
                <td className="paradigm-cell paradigm-cell--empty" key={index}></td>
            );
        } else if (cell.should_suppress_output) {
            const class_name = "paradigm-label paradigm-label--row";
            return (
                <th
                    scope={"row"}
                    rowSpan={1}
                    className={class_name}
                    key={counter.toString() + '-' + index.toString()}
                >
                </th>
            );
        } else {
            let displayText = cell.inflection[type];
            if (settings.morphemes_everywhere || settings.morphemes_paradigms) {
                displayText = cell.morphemes[type].join("/");
            }
            const class_name =
                "paradigm-cell paradigm-cell--" +
                (cell.observed ? "observed" : "unobserved");
            const recording = cell.recording || "";
            if (recording && showAudio) {
                function playRecording() {
                    const audio = new Audio(recording.recording_url);
                    audio.play();
                }

                return (
                    <td className={class_name} key={index}>
                        {displayText}&nbsp;
                        <button onClick={playRecording}>&#9655;</button>
                    </td>
                );
            } else {
                return (
                    <td className={class_name} key={index}>
                        {displayText}
                    </td>
                );
            }
        }
    });
    return <tr className="paradigm-row">{cell_layouts}</tr>;
}

export default SingleColumnRow;
