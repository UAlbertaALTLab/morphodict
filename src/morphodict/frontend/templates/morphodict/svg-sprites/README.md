For icons, we define all of the SVGs into one big file that's included
into every page. This way, all the icons are loaded always, and they're
easy to style using CSS.

To convert a FontAwesome icon into an SVG sprite:

 * create a `<symbol>` for it in ../svg-sprites.html
 * move its `viewport=` attribute to the newly created `<symbol>`
 * edit the SVG and delete the start and end `<svg></svg>` tags, leaving
   behind only `<path>` tags.

See: https://css-tricks.com/svg-symbol-good-choice-icons/#article-header-id-1
