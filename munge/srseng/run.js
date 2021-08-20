#!/usr/bin/env node

/*
 * A launcher script for toimportjson.ts that sets up run-time transpilation.
 */

const { runHelper } = require("../shared/run-helper");

runHelper("toimportjson.ts");
