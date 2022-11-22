import "../style.css";
import Pane from "./Pane";
import SingleColumnPane from "./SingleColumnPane";
import Labels from "./labels.json";
import {useState, useEffect} from "react";
import {Grid} from "@mui/material";
import {useLocation} from "react-router-dom/cjs/react-router-dom.min";

function Paradigm(state) {
    const panes = state.paradigm.panes;
    const type = state.type;
    let counter = 0;

    // let settings = JSON.parse(window.localStorage.getItem("settings"));
    // let type = "Latn";
    // if (settings.latn_x_macron) {
    //     type = "Latn-x-macron";
    // }
    // if (settings.syllabics) {
    //     type = "Cans";
    // }

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
                        console.log("ROW CELLS K", row.cells[k])

                        row_resolved_inflection.inflection = row.cells[k].inflection;

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

        if (pane_columns_buffer) {
            pane_columns.push(...pane_columns_buffer);
        }
    }

    const pane_layouts = pane_columns.map((pane_column, i) => {
        counter += 1;
        return (
            <div data-cy="paradigm" className="col-sm-12 col-md-6 col-lg-4" key={counter.toString() + '-' + i.toString()}>
                <div className="card">
                    <SingleColumnPane pane={pane_column} counter={counter} type={type}></SingleColumnPane>
                </div>
            </div>
        );
    });

    return <div className="container"><div className={"row"}>{pane_layouts}</div></div>;
}

export default Paradigm;
