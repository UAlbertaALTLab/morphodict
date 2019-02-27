import React from 'react';

import './searchForm.css';

import { wordDetail, getData, getLoaded } from '../util';

import SearchDetail from "./searchDetail";

import PropTypes from "prop-types";

var loaded = false;

export const reset = () => {
    loaded = false;
}

class SearchList extends React.Component{
    /*static propTypes = {
        sended: PropTypes.boolean.isRequired,
        //this.props.sended
    };*/
    constructor(props) {
        super(props);

        this.state = {
            det: null,
            A: null,
            word: null,
        };
      }
    
    detail(item){
        //alert(item);
        loaded = true;
        this.setState({
            word: item,
        })
        wordDetail(item).then(response => {
            console.log(response)
            response.json().then(data => {
                console.log(JSON.stringify(data))
                this.setState({
                    det: data.inflections,
                }, () => console.log(this.state))
            })
        })
    }

    /*shouldComponentUpdate() {
        if (this.props.sended === true && !this.props.Words) {
            return true;
        }
        return false;
      }*/

    render(props) {
        console.log('prop sended: ' + this.props.sended);
        console.log('Data sended: ' + JSON.stringify(this.props.Words));
        if (!this.props.Words) {
            console.log('prop sended: ' + this.props.sended);
            console.log('Data sended: ' + JSON.stringify(this.props.Words));
            return (<div><h1>Error page</h1></div>);
        }
        if (this.props.Words && this.props.sended && !loaded) {
            return (
                <div className="centre"> 
                <section>
                    <ul className="centreli">
                        {this.props.Words.map((wordlist) => {
                                return <li key={wordlist.id} onClick={() => this.detail(wordlist.context)}>{wordlist.context}</li>
                            })
                        }
                    </ul>
                </section>
                </div>
            );
        }
        if (this.props.Words && loaded) {
            return (
                <div className="centre"> 
                <SearchDetail
                    det = {this.state.det}
                    word = {this.state.word}>
                </SearchDetail>
                </div>
            );
        }
      }
}

export default SearchList;

/*
onClick = {() => {this.props.onClick(catName)}}
{this.state.Words.map((task, i) => <li key={i}>{task.context}</li>)}

constructor () {
    super()

    this.state {
      tasks: null
    }
  }

  componentDidMount () {
    fetch('/task')
      .then((data) => {
        return data.json()
      })
      .then((json) => {
        this.setState({ tasks: json.tasks })
      })
  }

  renderTaskList () {
    if (this.state.tasks) {
      return (
        <ul>
          {this.state.tasks.map((task, i) => <li key={i}>{task.name}</li>)}
        </ul>
      )
    }

    return <p>Loading tasks...</p>
  }
    render () {
        return (
            <div>
            <h1>Tasks</h1>
            {this.renderTaskList()}
            </div>
        );
    }
*/