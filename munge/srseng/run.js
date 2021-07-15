#!/usr/bin/env node

/*
 * A launcher script for toimportjson.ts that sets up run-time transpilation.
 * Written in JS for windows compatibility.
 */

const { spawn } = require("child_process");
const { dirname, join } = require("path");

const argv = process.argv.slice();
const nodeExecutable = argv.shift();
const thisScript = argv.shift();

const targetScript = join(dirname(thisScript), "toimportjson.ts");

let child;

child = spawn(
  nodeExecutable,
  ["-r", "sucrase/register/ts", targetScript, ...argv],
  {
    stdio: "inherit",
  }
);
child.on("error", function (e) {
  throw e;
});
child.on("exit", function (code, signal) {
  if (code) {
    process.exit(code);
  }
  if (signal) {
    process.exit(1);
  }
});
