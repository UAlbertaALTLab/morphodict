import { useState } from "react";
import Row from "./Row";
import {
  Card,
  Collapse,
  Accordion,
  AccordionSummary,
  Typography,
  AccordionDetails,
  Grid,
} from "@mui/material";

function Pane(rows) {
  const row_list = rows.rows;
  const row_layouts = row_list
    .filter((row) => !row.is_header)
    .map((row) => <Row row={row}></Row>);

  const header_list = row_list
    .filter((row) => row.is_header)
    .map((header) => header.label);
  const header = header_list.join("/");

  const [isOpen, setIsOpen] = useState(true);
  return (
    <Grid container>
      <Grid item style={{ width: "100%" }}>
        <Accordion>
          <AccordionSummary aria-controls="panel1a-content" id="panel1a-header">
            <Typography style={{ width: "100%", textAlign: "center" }}>
              {header}
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography>
              <Card style={{ width: "100%" }}>
                {" "}
                <tbody>{row_layouts}</tbody>
              </Card>
            </Typography>
          </AccordionDetails>
        </Accordion>
      </Grid>
    </Grid>
  );
}
export default Pane;
