#!/usr/bin/env node

const { spawn } = require("child_process");
const { dirname, join } = require("path");

/**
 * Run targetScript, relative to the directory containing the ‘main’ node
 * script, with run-time transpilation set up.
 *
 * Written in JS for windows compatibility; otherwise it would be a short
 * shell script that did `exec node -r sucrase/ts/register foo.ts`.
 */
function runHelper(targetScript) {
  const argv = process.argv.slice();
  const nodeExecutable = argv.shift();
  const thisScript = argv.shift();

  const targetPath = join(dirname(thisScript), targetScript);

  let child;

  // There’s no exec()-style system call to replace the current process with
  // a new one in Windows, so we have to spawn a new process and wait for it
  // to exit.
  child = spawn(
    nodeExecutable,
    ["-r", "sucrase/register/ts", targetPath, ...argv],
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
}

module.exports = { runHelper };
