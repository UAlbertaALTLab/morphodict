/*
*   Adds input word at end and fetches on Url
*/

import React, { Component } from "react";

import {SearchURL, DetailURL} from '../config/url';

// Used for search word
export const searchWord = (word) => {
    const url = SearchURL + word;
    return fetch(url);
};

// Used to gain detail of selected word
export const wordDetail = (word) => {
    const url = DetailURL + word;
    return fetch(url);
};