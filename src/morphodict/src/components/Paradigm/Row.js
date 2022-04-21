function Row(props) {
  const cell_list = props.row.cells;
  const cell_layouts = cell_list.map((cell) => {
    if (cell.is_label) {
      const class_name = "paradigm-label paradigm-label--" + cell.label_for;
      return (
        <th
          scope={cell.label_for}
          rowSpan={cell.row_span}
          className={class_name}
        >
          {cell.label}
        </th>
      );
    } else if (cell.is_missing) {
      return <td className="paradigm-cell paradigm-cell--missing">&mdash;</td>;
    } else if (cell.is_empty) {
      return <td className="paradigm-cell paradigm-cell--empty"></td>;
    } else {
      const class_name =
        "paradigm-cell paradigm-cell--" +
        (cell.observed ? "observed" : "unobserved");
      return <td className={class_name}>{cell.inflection}</td>;
    }
  });
  return <tr className="paradigm-row">{cell_layouts}</tr>;
}
export default Row;
