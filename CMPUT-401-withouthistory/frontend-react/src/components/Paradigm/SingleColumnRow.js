
function SingleColumnRow(props) {
  const cell_list = props.cells;
  const labelType = props.labelType;
  const labels = props.labels;
  const cell_layouts = cell_list.map((cell, index) => {
    if (cell.is_label) {
      const class_name = "paradigm-label paradigm-label--" + cell.label_for;
      return (
        <th
          scope={cell.label_for}
          rowSpan={1}
          className={class_name}
          key={index}
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
          key={index}
        >
        </th>
      );
    } else {
      const class_name =
        "paradigm-cell paradigm-cell--" +
        (cell.observed ? "observed" : "unobserved");
      return (
        <td className={class_name} key={index}>
          {cell.inflection}
        </td>
      );
    }
  });
  return <tr className="paradigm-row">{cell_layouts}</tr>;
}

export default SingleColumnRow;
