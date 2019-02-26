import React, { Component } from "react";

import {SearchURL, DetailURL} from './url';

var loaded = true;

var data = [];

function connect(url) {
    fetch(url)
        .then(response => {
              if (response.status !== 200) {
                  loaded = false;
                  console.log(loaded);
                  return loaded;
              };
              return response.json();
              })
        .then(data => {
            data = data;
            console.log(data);
            return data;
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
    console.log(data);
    return data;
}

export const getLoaded = () => {
    console.log(data);
    return loaded;
}