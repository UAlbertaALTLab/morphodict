import "../style.css";
import Pane from "./Pane";
import SingleColumnPane from "./SingleColumnPane";
import Labels from "./labels.json";
import { useState, useEffect } from "react";
import { Grid } from "@mui/material";
import { useLocation } from "react-router-dom/cjs/react-router-dom.min";

function Paradigm(state) {
  const panes = state.paradigm.panes;

  const {height, width} = useWindowDimensions();
  const width_per_column = 400;
  const columns = Math.floor(width / width_per_column);

  let settings = JSON.parse(window.localStorage.getItem("settings"));
  let type = "Latn";
  if (settings.latn_x_macron) {
    type = "Latn-x-macron";
  }
  if (settings.syllabics) {
    type = "Cans";
  }

  // parsing the paradigm
  let pane_columns = [];
  for (let i = 0; i < panes.length; i++) {
    //for each panes
    let rows = panes[i].tr_rows;
    let num_of_columns = 0;
    let pane_columns_buffer = null;
    let header = null;
    for (let j = 0; j < rows.length; j++) {
      //for each row
      let row = rows[j];

      if (row.is_header) {
        header = row;
        continue;
      } else if (num_of_columns === 0) {
        num_of_columns = row.cells.length;
        pane_columns_buffer = Array(num_of_columns - 1);
        for (let k = 0; k < num_of_columns - 1; k++) {
          pane_columns_buffer[k] = {
            header: header,
            col_label: null,
            labels: [],
            cells: [],
          }
        }
      }

      let row_label = row.cells[0];
      let column_index = 0;
      for (let k = 1; k < row.cells.length; k++) {
        //for each column
        if (row.cells[k].is_label && row.cells[k].label_for === "col") {
          pane_columns_buffer[column_index].col_label = row.cells[k];
          column_index++;
        } else if (!row.cells[k].should_suppress_output) {
          // normal wordform (including empty)
          pane_columns_buffer[column_index].labels.push(row_label);
          let row_resolved_inflection = row.cells[k];

          if (!row.cells[k].is_missing) {
            try {
              row_resolved_inflection.inflection = row.cells[k].inflection[type];
            } catch {
              row_resolved_inflection.inflection = row.cells[k].inflection;
            }
          }

          pane_columns_buffer[column_index].cells.push(row_resolved_inflection);
          column_index++;
        } else {
          // multiple wordforms
          row_label = row.cells[k];
          column_index = 0;
        }
      }
    }
    pane_columns.push(...pane_columns_buffer);
  }
  let panes_columns_slice = [];
  let num_per_column = pane_columns.length / columns;
  for (let i = 0; i < columns; i++) {
    panes_columns_slice.push(
      pane_columns.slice(i * num_per_column, (i + 1) * num_per_column)
    );
  }

  const pane_layouts = panes_columns_slice.map((pane_column, i) => {
    return (
      <Grid item xs={12 / columns} key={i}>
        <Grid container>
          {pane_column.map((pane, j) => {
            return (
              <Grid item style={{ width: "100%" }} key={i * num_per_column + j}>
                <SingleColumnPane pane={pane}></SingleColumnPane>
              </Grid>
            );
          })}
        </Grid>
      </Grid>
    );
  });

  return <Grid container>{pane_layouts}</Grid>;
}

function useWindowDimensions() {

  const hasWindow = typeof window !== 'undefined';

  function getWindowDimensions() {
    const width = hasWindow ? window.innerWidth : null;
    const height = hasWindow ? window.innerHeight : null;
    return {
      width,
      height,
    };
  }

  const [windowDimensions, setWindowDimensions] = useState(getWindowDimensions());

  useEffect(() => {
    if (hasWindow) {
      function handleResize() {
        setWindowDimensions(getWindowDimensions());
      }

      window.addEventListener('resize', handleResize);
      return () => window.removeEventListener('resize', handleResize);
    }
  }, [hasWindow]);

  return windowDimensions;
}

export default Paradigm;
