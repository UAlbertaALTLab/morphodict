/**
 * PostCSS config.
 */

const postcssCustomProperties = require('postcss-custom-properties');
const postcssImport = require('postcss-import');

module.exports = {
  map: {inline: true},

  plugins: [
    /**
     * Inline @import rules (e.g., @import "normalize.css").
     */
    postcssImport(),
    /**
     * Turns CSS Custom Properties (a.k.a., variables) into old school
     * declarations. e.g.,
     *   :root {
     *    --my-var: blue;
     *   }
     *   p {
     *    color: var(--my-var);
     *   }
     *
     * becomes
     *
     *  p {
     *    color: blue;
     *    color: var(--my-var);
     *  }
     */
    postcssCustomProperties(),

    // NOTE: minification is handled by Rollup!
  ]
};
