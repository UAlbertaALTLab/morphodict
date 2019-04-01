import React from 'react';

import i18next from "../translate";

class NavNavBar extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            toggled: false,
        };
    }

    toggledBool(){
        this.setState({
            toggled: !this.state.toggled,
        })
    }

    toggled(){
        if (this.state.toggled === true){
            document.documentElement.classList.add("nav-open")
            return "navbar-toggle d-inline toggled"
        }else {
            document.documentElement.classList.remove("nav-open")
            return "navbar-toggle d-inline"
        }
    }

    //render
    render() {
        return (
            <div className="container-fluid">
                <div className="navbar-wrapper">
                    <div className={this.toggled()}>
                        <button type="button" className="navbar-toggler" onClick={() => this.toggledBool()}>
                            <span className="navbar-toggler-bar bar1"></span>
                            <span className="navbar-toggler-bar bar2"></span>
                            <span className="navbar-toggler-bar bar3"></span>
                        </button>
                    </div>
                </div>
            </div>
        );
    }

}

export default NavNavBar;