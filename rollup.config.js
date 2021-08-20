/**
 * Rollup config
 *
 * Creates the proper static files.
 */

import * as path from 'path'

require('dotenv').config();  // Load environment variables from .env

/////////////////////////////// Rollup plugins ///////////////////////////////
import {terser} from 'rollup-plugin-terser'
import resolve from 'rollup-plugin-node-resolve'
import commonjs from 'rollup-plugin-commonjs'
import postcss from 'rollup-plugin-postcss'


///////////////////////////////// Constants //////////////////////////////////

const BUILD_DIR = './generated/frontend/morphodict';

// Production mode when debug is false.
const production = !process.env.DEBUG;


/////////////////////////////////// Config ///////////////////////////////////

module.exports = [
  {
    input: "frontend/index.js",
    output: {
      file: path.join(BUILD_DIR, "js", "index.js"),
      name: null, // The script does not export anything.
      format: "iife",
      sourcemap: true,
    },
    plugins: [
      resolve(), // finds modules in node_modules
      commonjs(), // make rollup understand require() statements
      postcss({
        // Save the CSS here.
        extract: path.join(BUILD_DIR, "css", "styles.css"),
        minimize: production,
        sourcemap: true,
      }),
      production && terser(), // minify, but only in production
    ],
  },
  {
    input: "frontend/click-in-text-embedded-test.js",
    output: {
      file: path.join(BUILD_DIR, "js", "click-in-text-embedded-test.js"),
      name: null, // The script does not export anything.
      format: "iife",
      sourcemap: true,
    },
    plugins: [
      resolve(), // finds modules in node_modules
      commonjs(), // make rollup understand require() statements
    ]
  },
];
