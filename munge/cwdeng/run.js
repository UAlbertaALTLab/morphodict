#!/usr/bin/env node

/*
 * A launcher script for cwdize.ts that sets up run-time transpilation.
 */

const { runHelper } = require("../shared/run-helper");

runHelper("cwdize.ts");
