import React, { Component } from "react";

import {SearchURL, DetailURL} from './url';

var loaded = true;

var Data = null;

function connect(url) {
    fetch(url)
        .then(response => {
            if (response.status !== 200) {
                loaded = false;
                console.log('util loaded: ' + loaded);
                return loaded;
            };
            return response.json();
        })
        .then(data => {
            Data = data;
            loaded = true;
            console.log('util data: ' + JSON.stringify(Data));
            return Data;
        })
        .catch(function(error) {
            console.log('Error: ', error.message);
          });
};

export const searchWord = (word) => {
    loaded = false;
    const url = SearchURL + word;
    return fetch(url);
};

export const wordDetail = (word) => {
    loaded = false;
    const url = DetailURL + word;
    return fetch(url);
};

export const getData = () => {
    console.log('util getdata: ' + JSON.stringify(Data));
    return Data;
}

export const getLoaded = () => {
    console.log('util getLoaded: ' + loaded);
    return loaded;
}