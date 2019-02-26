import React, { Component } from "react";

import {SearchURL, DetailURL} from './url';

var loaded = true;

var Data = [];

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
            console.log('util data: ' + JSON.stringify(Data));
            return Data;
        })
        .catch(function(error) {
            console.log('Error: ', error.message);
          });
};

export const searchWord = (word) => {
    const url = SearchURL + word;
    connect(url);
};

export const wordDetail = (word) => {
    const url = DetailURL + word;
    return connect(url);
};

export const getData = () => {
    console.log('util getdata: ' + JSON.stringify(Data));
    return Data;
}

export const getLoaded = () => {
    console.log('util getLoaded: ' + loaded);
    return loaded;
}