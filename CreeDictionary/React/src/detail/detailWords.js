/*
* DetailWords class
*
*   Returns table fomat of Word detail of clicked word in SearchList
*/

import React from 'react';

import { wordDetail } from '../util';
import { withRouter } from 'react-router-dom';

import { sro2syllabics } from 'cree-sro-syllabics';
/*
var CreeSROSyllabics = require('cree-sro-syllabics')
console.log(CreeSROSyllabics.sro2syllabics("tân'si")) // logs ᑖᓂᓯ*/

class DetailWords extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            inflection: null,
            lemma: null,
            definition: null,
        };
    }

    //Search word again from table , for sprint 4
    //Add onClick={() => this.reSearch(key[1]) in <td className="td-actions text-left" key={key}>{key[1]}</td>
    reSearch(item) {
        event.preventDefault();
        this.props.history.push('/search/' + item);
    }

    // Check if sent object is empty
    isEmpty(obj) {
        for (var key in obj) {
            if (obj.hasOwnProperty(key))
                return false;
        }
        return true;
    }

    // Fetches on searching word 
    // set inflection to returned inflection data
    // set lemma to returned lemma data
    // set definition to returned list of definition
    gainDetail() {
        //alert(item);
        wordDetail(this.props.location.pathname.split('/')[2]).then(response => {
            console.log(response)
            response.json().then(data => {
                //console.log(JSON.stringify(data))
                this.setState({
                    inflection: data.inflections,
                    lemma: data.lemma,
                    definition: data.lemma.definitions,
                }, () => console.log(this.state))
            })
        })
        return this.state.list
    }

    // Checks if clicked word changed
    // if did reloads(reRender)
    componentDidUpdate(prevProps) {
        console.log(this.isEmpty(prevProps));
        //console.log(prevprops.location.pathname.split('/'));
        // Typical usage (don't forget to compare props):
        if (this.props.location.pathname.split('/')[2] !== prevProps.location.pathname.split('/')[2]) {
            //alert('its dif');
            this.gainDetail();
        }
    }

    getData(data, flag) {
        return new Promise(function (resolve, reject) {
            resolve(data)
        });
    }


    getParadigms() {
        var data = this.state.lemma.attributes
        //console.log(data,"GET PARADIGMS")
        this.getType(data, this.generateParadigms);
    }

    getType(data, callback) {
        var initialData = this.getData(this.state.lemma.attributes);

        let self = this;

        initialData.then(function (result) {
            var length = result.length;
            var inflections = [];
            for (var i = 0; i < length; i++) {
                inflections.push(result[i].name)
            }
            return inflections;

        }).then(function (result) {
            if (result.includes("N")) {
                if (result.includes("A")) {
                    if (result.includes("D")) {
                        return "nad"
                    } else {
                        return "na"
                    }
                } else if (result.includes("I")) {
                    if (result.includes("D")) {
                        return "nid"
                    } else {
                        return "ni"
                    }
                }
            } else if (result.includes("V")) {
                if (result.includes("TA")) {
                    return "vta"
                } else if (result.includes("TI")) {
                    return "vti"
                } else if (result.includes("AI")) {
                    return "vai"
                } else if (result.includes("II")) {
                    return "vii"
                }
            } else {
                return "null"
            }
        }).then(function (result) {
            //console.log(result,"GET TYPE");
            callback(result, self, self.fillParadigms);
        });
    }

    loadParadigm(type, layout, prev, loc) {
        return new Promise(function (resolve, reject) {

            var route = "/static/layouts/" + type + "-" + layout + ".layout.tsv"
            d3.text(route, function (textString) {
                prev[loc] = d3.tsvParseRows(textString);

                resolve(prev);
            });
        });
    }

    generateParadigms(type, context, callback) {
        if (typeof type !== undefined) {
            var prev = [[], [], []]

            var basicparadigm = context.loadParadigm(type, "basic", prev, 0);

            basicparadigm.then(function (result) {
                var extendedparadigm = context.loadParadigm(type, "extended", result, 1);

                extendedparadigm.then(function (result) {
                    var fullparadigm = context.loadParadigm(type, "full", prev, 2);

                    fullparadigm.then(function (result) {
                        callback(result, context, context.displayParadigms)
                    });
                });
            });
        }
    }

    replaceParadigm(data, loc, context, words) {
        {/*
			data: the unfilled paradigm tables received from fillParadigms
			loc: 0 represents the basic inflectional table, 1 represents the extended inflectional table, and 2 represents the full inflectional table
			context: the context of the application outside the callbacks
			words: the list of inflections and their equation
			
			Iterates through both the paradigm table and the inflectional word list to find matches between their paradigm equations,
			then sets the matched word as a replacement to the paradigm table.
		*/}

        var type = ['basic', 'extended', 'full'];
        return new Promise(function (resolve, reject) {

            var paradigm = data[loc];	/* Gets the data at the specific location to represent the particular inflectional form */

            for (var row = 0; row < paradigm.length; row++) {	/* Iterates through the rows of the paradigm table */
                for (var col = 1; col < paradigm[row].length; col++) {	/* Iterates through the columns of the paradigm table */
                    var equation = paradigm[row][col].split("+");	/* Splits the paradigm equation by "+" */
                    if (equation.length > 1) {	/* Checks if the column split by "+" is a paradigm equation (i.e. has more than 1 object) */
                        for (var word = 0; word < words.length; word++) { /* Iterates through each word of the inflection list (words) */
                            var matches = 0;	/* Matches is used to count the number of inflectional portions matches between the paradigm and the inflectional form */
                            var starfound = false;	/* To accomodate the inflectional equations that contain a "*" to represent one or more lemma forms */
                            for (var part = 0; part < equation.length; part++) {	/* Iterates through each inflectional portion within equation */
                                for (var word_eq = 0; word_eq < words[word][1].length; word_eq++) { /* Iterates through each inflectional equation portion connected to an inflectional form */
                                    if (equation[part] === "*") {	/* Found a "*" representing 0 or more lemma types */
                                        starfound = true;
                                    }
                                    if (equation[part] === words[word][1][word_eq]) {	/* A match is found, so increment matches */
                                        matches += 1;
                                    }
                                }
                            };
                            if (starfound) {
                                {/* 
									Because paradigm equations occasionally contain a "*" meaning any lemma type can exist within them,
									the lemma type is considered and the length of the matches will be adjusted to accomodate the 0 or more
									that the "*" allows for.
								 */}
                                if (words[word][1][1] === "V") {	/* the lemma type is vta, vti, vii, or vai */
                                    matches += 2;
                                } else if (words[word][1][1] === "N") { /* the lemma type is na, nad, ni, or nid */
                                    if (words[word][1][3] === "D") {
                                        matches += 3;
                                    } else {
                                        matches += 2;
                                    }
                                };
                            } else {
                                if (words[word][1][1] === "V") {	/* the lemma type is vta, vti, vii, or vai */
                                    matches += 2;
                                } else if (words[word][1][1] === "N") { /* the lemma type is na, nad, ni, or nid */
                                    matches += 3;
                                };
                            }
                            if (equation[0] === "Der/Dim") {
                                if (words[word][1][0] === "N" && words[word][1][3] === "D") {
                                    matches += 3;
                                } else {
                                    matches += 2;
                                }
                            }
                            if (matches === equation.length) {
                                paradigm[row][col] = words[word][0];	/* Sets the word in the paradigm table to the matches inflectional form */
                            };

                        }
                    }
                }
            }
            data[loc] = paradigm;
            resolve(data);
        });
    }

    fillParadigms(data, context, callback) {
        {/*
			data: the paradigm tables received from fillParadigms
			context: the context of the application outside the callbacks
			callback: the function to be called on completion of the promises
			
			Takes in the unfilled paradigm tables, and for each table, fills in the words to their inflective equation
		*/}

        var words = []

        for (var i = 0; i < context.state.inflection.length; i++) {
            var inflections = []

            for (var t = 0; t < context.state.inflection[i].inflectionForms.length; t++) {
                inflections.push(context.state.inflection[i].inflectionForms[t].name);
            }

            words.push([context.state.inflection[i].context, inflections]);
        }

        var basicparadigm = context.replaceParadigm(data, 0, context, words);

        basicparadigm.then(function (result) {
            var extendedparadigm = context.replaceParadigm(result, 1, context, words);

            extendedparadigm.then(function (result) {
                var fullparadigm = context.replaceParadigm(result, 2, context, words);

                fullparadigm.then(function (result) {
                    callback(data, context);
                });
            });
        });
    }

    generateTable = (data, element, context) => {
        {/*
			data: the paradigm tables received from displayParadigms
			element: the name of the table in the HTML generation
			context: the context of the application outside the callbacks
			
			Takes in the paradigm tables and generates HTML tables to be set for each Paradigm type 
		*/}
        var table = ''

        for (var i = 0; i < data.length; i++) {
            table += "<tr>";
            if (data[i][0] === undefined) {
                console.log("FOUND UNDEFINED");
            } else if (data[i][0] !== "") {
                table += "<td>" + data[i][0] + "</td>";

                for (var t = 1; t < data[i].length; t++) {
                    table += "<td>" + data[i][t] + "</td>";
                }
            } else if (data[i][1] === undefined) {
                console.log("FOUND UNDEFINED");
            } else if (data[i][1][0] === undefined) {
                console.log("FOUND UNDEFINED");
            } else if (data[i][1][0] === ":") {
                for (var t = 0; t < data[i].length; t++) {
                    table += "<th className='text-center'>" + data[i][t].substring(3, data[i][t].length - 1) + "</th>";
                }
            } else {
                var length = data[i].length;
                table += "<th colspan='" + length + "' className='text-center'>" + data[i][1] + "</th>";
            }
            table += "</tr>";
        }
        //table += '</table>';
        document.getElementById(element).innerHTML = table;
    }

    displayParadigms(data, context) {
        {/*
			data: the paradigm tables filled with their respective words received from fillParadigms
			context: the context of the application outside the callbacks
			
			For each paradigm (basic,extended, and full) it passes that paradigm to be generated by generateTable
		*/}
        if (typeof data === undefined) {
            console.log("RECEIVED UNDEFINED DATA", "DISPLAY PARADIGMS");
        } else {
            var types = ['basictable', 'extendedtable', 'fulltable'];
            for (var i = 0; i < data.length; i++) {
                context.generateTable(data[i], types[i], context);
            }
        }
    }

    // checks if component did mount
    componentDidMount() {
        this.gainDetail()
        console.log('called2');
    }

    //renders
    render() {
        console.log('Path : ' + this.props.location.pathname.split('/')[2]);
        // If definition is not empty and inflection is empty
        if ((this.isEmpty(this.state.inflection) === true) && (this.isEmpty(this.state.definition) === false)) {
            return (
                <div className="row">
                    <div className="col-12">
                        <section>
                            <h1>{this.props.location.pathname.split('/')[2]}</h1>
                        </section>
                        <div className="card">
                            <div className="card-header">
                                <h2 className="card-title">Definition</h2>
                            </div>
                            <section className="card-body">
                                {this.state.definition.map((e) => {
                                    return (
                                        <h3 key={e.id} className="text-center" >{e.context}<br /><sub>{e.source}</sub></h3>)
                                })}
                            </section>
                        </div>
                    </div>
                </div>
            );
        }

        // if both inflection and definition is not empty
        else if ((this.isEmpty(this.state.inflection) === false) && ((this.isEmpty(this.state.definition) === false))) {

            this.getParadigms();

            return (
                <div className="row">
                    <div className="col-12">
                        <section>
                            <h1>{this.props.location.pathname.split('/')[2]}<br />
                                <sub>{sro2syllabics(this.props.location.pathname.split('/')[2])}</sub></h1>
                        </section>
                        <div className="card">
                            <div className="card-header">
                                <h2 className="card-title">Definition</h2>
                            </div>
                            <section className="card-body">
                                {this.state.definition.map((e) => {
                                    return (
                                        <h3 key={e.id}>{e.context}<br /><sub>{e.source}</sub></h3>)
                                })}
                            </section>
                        </div>
                    </div>
                    <div className="col-12">
                        <details id="basic" className="card">
                            <summary className="card-header"><strong>Basic</strong></summary>
                            <div className="table-responsive">
                                <table id="basictable" className="table" border="1" >
                                </table>
                            </div>
                        </details>
                        <details id="extended" className="card">
                            <summary className="card-header"><strong>Extended</strong></summary>
                            <div className="table-responsive">
                                <table id="extendedtable" className="table" border="1">
                                </table>
                            </div>
                        </details>
                        <details id="full" className="card">
                            <summary className="card-header"><strong>Full</strong></summary>
                            <div className="table-responsive">
                                <table id="fulltable" className="table" border="1">
                                </table>
                            </div>
                        </details>
                    </div>
                </div>
            );
        }
        //if both inflection and definition is empty
        else {
            return (<div><h1>{this.props.location.pathname.split('/')[2]}</h1></div>)
        }
    }
}

export default withRouter(DetailWords);
