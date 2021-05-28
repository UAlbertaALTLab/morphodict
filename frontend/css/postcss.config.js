/**
 * PostCSS config.
 */

const postcssImport = require('postcss-import')

module.exports = {
  map: {inline: true},

  plugins: [
    /**
     * Inline @import rules (e.g., @import "normalize.css").
     */
    postcssImport(),
    // NOTE: minification is handled by Rollup!
  ]
}
/* eslint-env node */
