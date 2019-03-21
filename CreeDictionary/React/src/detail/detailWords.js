/*
* DetailWords class
*
*   Returns table fomat of Word detail of clicked word in SearchList
*/

import React from 'react';

import { wordDetail } from '../util';
import { withRouter } from 'react-router-dom';

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

    isEmpty(obj) {
        for (var key in obj) {
            if (obj.hasOwnProperty(key))
                return false;
        }
        return true;
    }

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

    componentDidUpdate(prevProps) {
        console.log(this.isEmpty(prevProps));
        //console.log(prevprops.location.pathname.split('/'));
        // Typical usage (don't forget to compare props):
        if (this.props.location.pathname.split('/')[2] !== prevProps.location.pathname.split('/')[2]) {
            //alert('its dif');
            this.gainDetail();
        }
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
		//console.log(type,"GENERATE PARADIGMS");
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
		var type = ['basic','extended','full'];
		return new Promise(function(resolve,reject) {
			
			var paradigm = data[loc];
						
			
			
			for (var i=0;i<paradigm.length;i++){
				for (var t=1;t<paradigm[i].length;t++){
					var equation = paradigm[i][t].split("+");
					if (equation.length > 1){
						for (var a=0;a<words.length;a++){
							var matches = 0;
							var starfound = false;
							for (var q=0;q<equation.length;q++){
								for (var m=0;m<words[a][1].length;m++){
									if (equation[q] === "*"){
										starfound = true;
									}
									if (equation[q] === words[a][1][m]){
										matches += 1;
									}
								}
							};
							if (starfound){
								if (words[a][1][1] == "V"){
									matches += 2;
								} else if (words[a][1][1] == "N"){
									matches += 3;
								}
							}
							if (matches === equation.length){
								paradigm[i][t] = words[a][0];
							} else {
							};
						}
					}
				}
			}		
			resolve(data);
		});
	}
	
	fillParadigms(data,context,callback){
		//console.log(data,"FILL PARADIGMS");
		
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
		if (typeof data === undefined){
			console.log("RECEIVED UNDEFINED DATA","DISPLAY PARADIGMS");
		}else {
			var types = ['basictable','extendedtable','fulltable'];
			for (var i=0;i<data.length;i++){
				context.generateTable(data[i],types[i],context);
			}
		}
	}
	

    componentDidMount() {
        this.gainDetail()
        console.log('called2');
    }

    //renders
    render() {
        console.log('Path : ' + this.props.location.pathname.split('/')[2]);
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

	else if ((this.isEmpty(this.state.inflection) === false) && ((this.isEmpty(this.state.definition) === false))) {
	    this.getParadigms();
	    
	    return (<div className="row">
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
                                        <h3 key={e.id}>{e.context}<br /><sub>{e.source}</sub></h3>)
                                })}
	    </section>
    </div>
      	
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
        }
        else {
            return (<div><h1>{this.props.location.pathname.split('/')[2]}</h1></div>)
        }
    }
}

export default withRouter(DetailWords);
