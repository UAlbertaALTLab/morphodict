import { useState, useEffect } from "react";
import Row from "./Row";
import SingleColumnRow from "./SingleColumnRow";
import {
  Card,
  Collapse,
  Accordion,
  AccordionSummary,
  Typography,
  AccordionDetails,
  Grid,
} from "@mui/material";
import Labels from "../../layouts/crk.altlabel.json";

function SingleColumnPane(props) {
  const pane = props.pane;
  let counter = props.counter;
  let defaultLabel = JSON.parse(window.localStorage.getItem("settings")).label;
  if (!defaultLabel) {
    defaultLabel = "ENGLISH";
  }
  const [labelType, setLabelType] = useState(defaultLabel);

  let labels = {}
  Labels.map((items) => {
      labels[items["FST TAG"]] = {
        "LINGUISTIC (SHORT)": items["LINGUISTIC (SHORT)"],
        "LINGUISTIC (LONG)": items["LINGUISTIC (LONG)"],
        "ENGLISH": items["ENGLISH"],
        "NÊHIYAWÊWIN": items["NÊHIYAWÊWIN"],
        "EMOJI": items["EMOJI"]
      }
    }
  );

  const defaultHeader = "Core";

  useEffect(() => {
    const handleLabelSetting = (e) => {
      let settings = JSON.parse(window.localStorage.getItem("settings"));
      setLabelType(settings.label);
    }
    window.addEventListener("settings", handleLabelSetting);
    return _ => window.removeEventListener("settings", handleLabelSetting)
  });

  const header = pane.header;
  const col_label = pane.col_label;
  let rows = [];
  for (let i = 0; i < pane.cells.length; i++) {
    rows.push(Array(pane.labels[i], pane.cells[i]));
  }

  const row_layouts = rows.map((row, index) => {
    return (
      <SingleColumnRow
        cells={row}
        labelType={labelType}
        labels={labels}
        counter={counter}
        key={counter.toString() + '-' + index.toString()}
      ></SingleColumnRow>
    );
  });

  return (
    <Accordion style={{ minHeight: "4.5em", width: "100%" }}>
      <AccordionSummary aria-controls="panel1a-content" id="panel1a-header">
        <div style={{ margin: "auto" }}>
          <Typography style={{ width: "100%", textAlign: "center" }}>
            {header == null ? defaultHeader : labels[header["label"].join("+")][labelType]}
          </Typography>
          <Typography
            style={{
              width: "100%",
              textAlign: "center",
              fontWeight: "bold",
            }}
          >
            {col_label == null
              ? null
              : labels[col_label["label"].join("+")][labelType]}
          </Typography>
        </div>
      </AccordionSummary>
      <AccordionDetails>
        <Card style={{ width: "100%" }}>
          <div className="card-body">
          {" "}
          <table className="paradigm-table">
            <tbody>{row_layouts}</tbody>
          </table>
          </div>
        </Card>
      </AccordionDetails>
    </Accordion>
  );
}
export default SingleColumnPane;
