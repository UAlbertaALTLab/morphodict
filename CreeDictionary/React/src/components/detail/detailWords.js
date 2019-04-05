/*
* DetailWords class
*
*   Returns table fomat of Word detail of clicked word in SearchList
*/

import React from 'react';

import { withRouter } from 'react-router-dom';

import { wordDetail } from '../../utils/network';
import i18next from '../../utils/translate';

import Definition from './definition';
import { sro2syllabics } from 'cree-sro-syllabics';

import ReactDOM from "react-dom";
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

    getParadigms(paradigm,words) {
    	{/*
    		paradigm: the type of the paradigm to be generated
    		words: the list of inflectional forms retrieved
    		
    		Begins the rendering process for the inflectional tables
    	*/}
    	
        this.getType(paradigm,words,this.generateParadigms);
    }

    getType(paradigm,words,callback) {
    	{/*
    		paradigm: the type of the paradigm to be generated
    		words: the list of inflectional forms retrieved
    		callback: the function to be called on completion of the promises (generateParadigms)
    		
    		Finds the type of the found word, so that the correct tables can be accessed
    	*/}
        
        var length = this.state.lemma.attributes.length;
        var inflections = [];
        var type = "null";
        
        //Assembles the type of the word
        for (var i = 0; i < length; i++) {
            inflections.push(this.state.lemma.attributes[i].name)
        }
        
        //Determines the inflectional type based on the assembled equation
        if (inflections.includes("N")) {
            if (inflections.includes("A")) {
                if (inflections.includes("D")) {
                    type = "nad"
                } else {
                    type = "na"
                }
            } else if (inflections.includes("I")) {
                if (inflections.includes("D")) {
                    type = "nid"
                } else {
                    type = "ni"
                }
            }
        } else if (inflections.includes("V")) {
            if (inflections.includes("TA")) {
                type = "vta"
            } else if (inflections.includes("TI")) {
                type = "vti"
            } else if (inflections.includes("AI")) {
                type = "vai"
            } else if (inflections.includes("II")) {
                type = "vii"
            }
        }
        
        var context = this;
        
        callback(type,words, paradigm, context, context.fillParadigms);
        
    }

    generateParadigms(type, words, paradigm, context, callback) {
    	{/*
    		type: the type of the word found
    		words: the list of inflections and their equations
    		paradigm: the type of the paradigm to be generated
    		context: the context of the application outside the callbacks
    		callback: the function to be called on completion of the promises (fillParadigms)
    		
    		Fetches the paradigm layout file from the server and converts them to an array
    	*/}
    	
    	var filled;

        var route = "/static/layouts/" + type + "-" + paradigm + ".layout.tsv"
        d3.text(route, function (textString) {
            filled = d3.tsvParseRows(textString);

            callback(filled,words,context, paradigm, context.displayParadigms)
        });
    	
    }

    fillParadigms(data, words, context, paradigm, callback) {
        {/*
			data: the paradigm tables received from fillParadigms
			context: the context of the application outside the callbacks
			callback: the function to be called on completion of the promises (displayParadigms)
			
			Iterates through both the paradigm table and the inflectional word list to find matches between their paradigm equations,
			then sets the matched word as a replacement in the paradigm table.
		*/}
        for (var row=0;row<data.length;row++){
			for (var col=1;col<data[row].length;col++){
				if(data[row][col].includes("+")){
					var matched = false;
					for(var word=0;word<words.length;word++){
						if (words[word][1].includes(data[row][col])){
							data[row][col] = words[word][0];
							matched = true;
							break;
						}
					}
					if(matched === false){
						data[row][col] = "N/A";
					}
				}
			}
		}
		
		callback(data, paradigm, context);
        
    }

    displayParadigms(data, paradigm,context) {
        {/*
			data: the paradigm table filled with their respective words received from fillParadigms
			context: the context of the application outside the callbacks
			
			Renders the paradigm tables into HTML through ReactDOM.render
		*/}
        if (typeof data === undefined) {
            console.log("RECEIVED UNDEFINED DATA", "DISPLAY PARADIGMS");
        } else {
            var name = paradigm+"table"

            var num = 0;
    		const table = (
				<tbody>
					{data.map((row) => {
						num +=1;
						var num2 = 0;
						return(
							<tr key={num}>
								{Object.entries(row).map((col) => {
									var thiscol = col[1];
									num2 += 1;
									if (thiscol[0] === undefined){
										console.log("FOUND UNDEFINED");
									} else if (thiscol[0] === ":"){
										thiscol = thiscol.substring(3, thiscol.length - 1)
										return<th key={num2}>{thiscol}</th>
									} else if (thiscol[0] === thiscol[0].toUpperCase()){
										return<th key={num2}>{thiscol}</th>
									} else {
										return<td key={num2}>{thiscol}</td>
									}
								})}
							</tr>
						);
					})}
				</tbody>
		
			);
    		ReactDOM.render(table,document.getElementById(name));
        }
    }
    
    getInflections(){
    	{/*
    		Gets the inflections and converts them to equation form for matching with the paradigm tables
    	*/}
    
    	var words = []

        for (var i = 0; i < this.state.inflection.length; i++) {
			var equation = "=";
            for (var t = 0; t < this.state.inflection[i].inflectionForms.length; t++) {
            	if (equation === "="){
                	equation += this.state.inflection[i].inflectionForms[t].name
                } else {
                	equation += "+" + this.state.inflection[i].inflectionForms[t].name
                }
            }

            words.push([this.state.inflection[i].context, equation]);
       	}
       	return words;
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
                    <Definition
                    word = {this.props.location.pathname.split('/')[2]}
                    definition = {this.state.definition}
                    />
                </div>
            );
        }

        // if both inflection and definition is not empty
        else if ((this.isEmpty(this.state.inflection) === false) && ((this.isEmpty(this.state.definition) === false))) {


			var words = this.getInflections();
       		
            this.getParadigms("basic",words);
        	this.getParadigms("extended",words);
            this.getParadigms("full",words);

            return (
                <div className="row">
                    <Definition
                    word = {this.props.location.pathname.split('/')[2]}
                    definition = {this.state.definition}
                    />
                    <div className="col-12">
                        <details id="basic" className="card">
                            <summary className="card-header"><strong>{i18next.t('Basic')}</strong></summary>
                            <div className="table-responsive">
                                <table id="basictable" className="table" border="1">
                                </table>
                            </div>
                        </details>
                        <details id="extended" className="card">
                            <summary className="card-header"><strong>{i18next.t('Extended')}</strong></summary>
                            <div className="table-responsive">
                                <table id="extendedtable" className="table" border="1">
                                </table>
                            </div>
                        </details>
                        <details id="full" className="card">
                            <summary className="card-header"><strong>{i18next.t('Full')}</strong></summary>
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
