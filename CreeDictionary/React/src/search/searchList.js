import React from 'react';

import './searchForm.css';

import { wordDetail, getData, getLoaded } from '../util';

import PropTypes from "prop-types";

class SearchList extends React.Component{
    /*static propTypes = {
        sended: PropTypes.boolean.isRequired,
        //this.props.sended
    };*/
    constructor(props) {
        super(props);

        this.state = {
            Words: [],
        };
        
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
      }
    
      handleChange(event) {
        this.setState({value: event.target.value});
      }
    
      handleSubmit(event) {
        event.preventDefault();
        //const data = new FormData(event.target);
        this.setState({
            sended: true,
        });
        searchWord(this.state.value);
        if (getLoaded() === false) {
          alert('Word not sent');
          console.log(getLoaded());
        }
      }

      getClassNames() {
        let classNames = 'search';
        if (this.state.sended === true) {
          classNames += 'isTrue';
        }
        return classNames;
      }

      renderTaskList () {
        if (this.props.sended === true) {
            if (getData() === []) {
                return <p>No Result</p>
            }
            else {
                this.setState({ Words: getData().words });
            }
        }
        if (this.state.Words) {
          return (
            <ul>
              {this.state.Words.map((words, i) => <li key={i}>{words.context}</li>)}
            </ul>
          )
        }
    
        return <p>Loading tasks...</p>
      }

      /*StateChange () {
        this.setState({ Words: getData().words})
        return <ul>{this.state.Words}</ul>
        if (this.props.sended === true) {
            this.setState({ Words: getData().words});
            /*
            if (getData() === []) {
                return <p>No Result</p>
            }
            else {
                this.setState({ Words: getData().words});
                return <ul>{this.state.Words}</ul>
            }
      }
    }*/

    shouldComponentUpdate() {
        if ((this.props.sended === true) && (getData().words !== this.state.Words)) {
            return true;
        }
        return false;
      }

    componentDidUpdate() {
        if (getData().words !== this.state.Words){
            this.setState({ Words: getData().words});
        }
    }

    render() {
        console.log('prop sended: ' + this.props.sended);
        console.log('Data sended: ' + JSON.stringify(getData()));
        console.log(this.state.Words);
        return (
            <div>
                <ul>
                    {this.state.Words.map(function(wordlist){
                            return <li key={wordlist.id}>{wordlist.context}</li>;
                        })
                    }
                </ul>
            </div>
        );
      }
}

export default SearchList;

/*
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