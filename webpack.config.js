const path = require('path');
// noinspection JSUnresolvedFunction
require('dotenv').config();

module.exports = {

    mode: process.env.DEBUG ? "development" : "production",

    entry: {
        index: './src/index.js',
    },

    output: {
        filename: "[name].js",
        path: path.resolve(__dirname, "CreeDictionary/CreeDictionary/static/CreeDictionary/js"),
    }
};