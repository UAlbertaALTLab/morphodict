/*
* DetailWords class
*
*   Returns table fomat of Word detail of clicked word in SearchList
*/

import React from 'react';

import SearchList from '../search/searchList';

import { reset } from '../search/searchList';
import { searchWord } from '../util';

var sended = false;

export const reset2 = () => {
    sended = false;
}

class DetailWords extends React.Component {

    constructor(props) {
        super(props);
        this.Words = null;
      }

    reSearch(item) {
        sended = true;
        reset();
        searchWord(item).then(response => {
            console.log(response)
            response.json().then(data => {
              //console.log(JSON.stringify(data))
              this.setState({
                Words: data.words,
              }, () => console.log(this.state))
            })
        });
    }

    isEmpty(obj) {
        for(var key in obj) {
            if(obj.hasOwnProperty(key))
                return false;
        }
        return true;
    }
    
    getData(data,flag){
    	return new Promise(function(resolve,reject) {
        	resolve(data)
        });
    }
    
    
    getParadigms(){
    	var data = this.props.lem.attributes
    	//console.log(data,"GET PARADIGMS")
    	this.getType(data,this.generateParadigms);
    }
    
    getType(data,callback){
		var initialData = this.getData(this.props.lem.attributes);
        	
        let self = this;
        	
        initialData.then(function(result){
        	var length = result.length;
    		var inflections = [];
    		for (var i=0;i<length;i++){
    			inflections.push(result[i].name)
    		}
    		return inflections;
    			
        }).then(function(result){
        	if (result.includes("N")){
    			if (result.includes("A")){
    				if (result.includes("D")){
    					return "nad"
    				} else {
    					return "na"
    				}
    			} else if(result.includes("I")){
    				if (result.includes("D")){
    						return "nid"
    				} else {
    					return "ni"
    				}
    			}
    		} else if (result.includes("V")){
    			if (result.includes("TA")){
    				return "vta"
    			}else if (result.includes("TI")){
    				return "vti"
    			} else if (result.includes("AI")){
    				return "vai"
    			} else if (result.includes("II")){
    				return "vii"
    			}
   	 		} else {
    			return "null"
    		}
        }).then(function(result){
        	//console.log(result,"GET TYPE");
			callback(result,self,self.fillParadigms);
        });    
	}
	
	loadParadigm(type,layout,prev,loc){
		return new Promise(function(resolve,reject) {
			
			var route = "/static/layouts/"+type+"-"+layout+".layout.tsv"
			d3.text(route,function(textString){
    			prev[loc] = d3.tsvParseRows(textString);
    			
    			resolve(prev);
    		});
    	});
    }
	
	generateParadigms(type,context,callback){
		if (typeof type !== undefined){
			var prev = [[],[],[]]
			
			var basicparadigm = context.loadParadigm(type,"basic",prev,0);
			
			basicparadigm.then(function(result){
				var extendedparadigm = context.loadParadigm(type,"extended",result,1);
				
				extendedparadigm.then(function(result){
					var fullparadigm = context.loadParadigm(type,"full",prev,2);
					
					fullparadigm.then(function(result){
						callback(result,context,context.displayParadigms)
					});
				});
			});
		}
	}
	
	replaceParadigm(data,loc,context,words){
		{/*
			data: the unfilled paradigm tables received from fillParadigms
			loc: 0 represents the basic inflectional table, 1 represents the extended inflectional table, and 2 represents the full inflectional table
			context: the context of the application outside the callbacks
			words: the list of inflections and their equation
			
			Iterates through both the paradigm table and the inflectional word list to find matches between their paradigm equations,
			then sets the matched word as a replacement to the paradigm table.
		*/}
	
		var type = ['basic','extended','full'];
		return new Promise(function(resolve,reject) {
			
			var paradigm = data[loc];	/* Gets the data at the specific location to represent the particular inflectional form */
						
			for (var row=0;row<paradigm.length;row++){	/* Iterates through the rows of the paradigm table */
				for (var col=1;col<paradigm[row].length;col++){	/* Iterates through the columns of the paradigm table */
					var equation = paradigm[row][col].split("+");	/* Splits the paradigm equation by "+" */
					if (equation.length > 1){	/* Checks if the column split by "+" is a paradigm equation (i.e. has more than 1 object) */
						for (var word=0;word<words.length;word++){ /* Iterates through each word of the inflection list (words) */
							var matches = 0;	/* Matches is used to count the number of inflectional portions matches between the paradigm and the inflectional form */
							var starfound = false;	/* To accomodate the inflectional equations that contain a "*" to represent one or more lemma forms */
							for (var part=0;part<equation.length;part++){	/* Iterates through each inflectional portion within equation */
								for (var word_eq=0;word_eq<words[word][1].length;word_eq++){ /* Iterates through each inflectional equation portion connected to an inflectional form */
									if (equation[part] === "*"){	/* Found a "*" representing 0 or more lemma types */
										starfound = true;
									}
									if (equation[part] === words[word][1][word_eq]){	/* A match is found, so increment matches */
										matches += 1;
									}
								}
							};
							if (starfound){
								{/* 
									Because paradigm equations occasionally contain a "*" meaning any lemma type can exist within them,
									the lemma type is considered and the length of the matches will be adjusted to accomodate the 0 or more
									that the "*" allows for.
								 */}
								if (words[word][1][1] === "V"){	/* the lemma type is vta, vti, vii, or vai */
									matches += 2;
								} else if (words[word][1][1] === "N"){ /* the lemma type is na, nad, ni, or nid */
									if (words[word][1][3] === "D"){
										matches += 3;
									} else {
										matches += 2;
									}
								};
							} else {
								if (words[word][1][1] === "V"){	/* the lemma type is vta, vti, vii, or vai */
									matches += 2;
								} else if (words[word][1][1] === "N"){ /* the lemma type is na, nad, ni, or nid */
									matches += 3;
								};
							}
							if (equation[0] === "Der/Dim"){
								if (words[word][1][0] === "N" && words[word][1][3] === "D"){
									matches += 3;
								} else {
									matches += 2;
								}
							}
							if (matches === equation.length){
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
	
	fillParadigms(data,context,callback){
		{/*
			data: the paradigm tables received from fillParadigms
			context: the context of the application outside the callbacks
			callback: the function to be called on completion of the promises
			
			Takes in the unfilled paradigm tables, and for each table, fills in the words to their inflective equation
		*/}
		
		var words = []

		for (var i=0;i<context.props.det.length;i++){
			var inflections = []

			for (var t=0;t<context.props.det[i].inflectionForms.length;t++){
				inflections.push(context.props.det[i].inflectionForms[t].name);
			}
			
			words.push([context.props.det[i].context,inflections]);
		}

		var basicparadigm = context.replaceParadigm(data,0,context,words);
		
		basicparadigm.then(function(result){
			var extendedparadigm = context.replaceParadigm(result,1,context,words);
				
			extendedparadigm.then(function(result){
				var fullparadigm = context.replaceParadigm(result,2,context,words);
					
				fullparadigm.then(function(result){
					callback(data,context);
				});
			});
		});
	}
	
	generateTable = (data,element,context) => {
		{/*
			data: the paradigm tables received from displayParadigms
			element: the name of the table in the HTML generation
			context: the context of the application outside the callbacks
			
			Takes in the paradigm tables and generates HTML tables to be set for each Paradigm type 
		*/}
    	var table = ""
    	
    	for (var i=0;i<data.length;i++){
    		table += "<tr>";
    		if (data[i][0] === undefined){
    			console.log("FOUND UNDEFINED");
    		}else if (data[i][0] !== ""){
    			table += "<td>"+data[i][0]+"</td>";
    			
    			for (var t=1;t<data[i].length;t++){
    				table += "<td>"+data[i][t]+"</td>";
    			}
    		}else if (data[i][1] === undefined){
    			console.log("FOUND UNDEFINED");
    		}else if ( data[i][1][0] === undefined){
    			console.log("FOUND UNDEFINED");
    		}else if (data[i][1][0] === ":"){
    			for (var t=0;t<data[i].length;t++){
    				table += "<th className='text-center'>"+data[i][t].substring(3,data[i][t].length-1)+"</th>";
    			}
    		} else {
    			var length = data[i].length;
    			table += "<th colspan='"+length+"' className='text-center'>"+data[i][1]+"</th>";
    		}
    		table += "</tr>";
    	}
    	document.getElementById(element).innerHTML = table;
    }
	
	displayParadigms(data,context){
		{/*
			data: the paradigm tables filled with their respective words received from fillParadigms
			context: the context of the application outside the callbacks
			
			For each paradigm (basic,extended, and full) it passes that paradigm to be generated by generateTable
		*/}
		if (typeof data === undefined){
			console.log("RECEIVED UNDEFINED DATA","DISPLAY PARADIGMS");
		}else {
			var types = ['basictable','extendedtable','fulltable'];
			for (var i=0;i<data.length;i++){
				context.generateTable(data[i],types[i],context);
			}
		}
	}
	
    //renders
    render(props) {
        console.log('Detail: ' + JSON.stringify(this.props.det));
        console.log('Detail2: ' + this.isEmpty(this.props.det));
        console.log('lemma: ' + JSON.stringify(this.props.lem));
        
        //While loading data returns below 
        if (!this.props.det) {
            return (
                <div className="container">
                    <section>
                        <h1>{this.props.word}</h1>
                    </section>
                </div>
            );
        }

        if (this.isEmpty(this.props.det) === true) {
            return (
                <div className="container">
                    <section>
                        <h1>{this.props.word}</h1>
                    </section>
                    <section>
                    {this.props.lem.definitions.map(e => (<p key={e.id}>{e.context}</p>))}
                    </section>
                </div>
            );
        }

        if (sended===true){
            return (
            <SearchList
                Words={this.state.Words}>
            </SearchList>
            );
        }
        
        //returns in Table Format
        
        if (this.props.det !== []) {
        	
        	this.getParadigms();
        	
            return (	
                <div className="table-responsive">
                    <section>
                        <h1>{this.props.word}</h1>
                    </section>
                    <section>
                    {this.props.lem.definitions.map(e => (<p key={e.id}>{e.context}</p>))}
                    </section>
                	<div>
                		<div id="basic">
                			<h1>Basic</h1>
                			<table id = "basictable" classname = "table" border = "1" >
                			</table>
                		</div>
                		<div id="extended">
                			<h1>Extended</h1>
                			<table id = "extendedtable" classname = "table" border = "1">
                			</table>
                		</div>
                		<div id="full">
                			<h1>Full</h1>
                			<table id = "fulltable" classname = "table" border = "1">
                			</table>
                		</div>
                	</div>
                </div>
            );
        } else{
                return(<p>N</p>);
            }
        }
    }

export default DetailWords;

/* Please ignore
return (
            <div className="centre">
                <div>
                    <h1>{this.props.word}</h1>
                </div>
                <section>
                    <ul className="centreli">
                        {this.props.det.map((wordlist) => {
                                return <li key={wordlist.id}>{wordlist.context}</li>
                            })
                        }
                    </ul>
                </section>
            </div>
        );
        
        
        
        
        <table className="table">
                        <thead>
                            <tr>
                                {Object.entries(this.props.det[0]).map((key, val) => <th class="text-center" key={key}>{key[0]}</th>)}
                            </tr>
                        </thead>
                        <tbody>
                            {this.props.det.map(e => (
                                <tr key={e.id}>
                                    {Object.entries(e).map((key, val) => {
                                        if (key[0] === "inflectionForms") {
                                            return <td className="text-left" key={key}>Object</td>
                                        }
                                        if (key[0] === "context"){
                                            return <td className="td-actions text-left" key={key} onClick={() => this.reSearch(key[1])}>{key[1]}</td>
                                        }
                                        return <td className="text-left" key={key}>{key[1]}</td>
                                    })
                                    }
                                </tr>
                            ))}
                        </tbody>
                    </table>
*/