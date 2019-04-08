import React from 'react';

import i18next from '../../utils/translate';

class NavSideBar extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            Lang: "en",
        };
    }

    translate(lan) {
        if (lan === "cree") {
            this.setState({
                Lang: "cree"
            })
        } else if (lan === "syllabic") {
            this.setState({
                Lang: "syllabic"
            })
        } else {
            this.setState({
                Lang: "en"
            })
        }
        this.props.language(this.state.Lang);
    }

    componentDidUpdate(prevProps, prevState) {
        // Typical usage (don't forget to compare state):
        if (this.state.Lang !== prevState.Lang) {
            this.props.language(this.state.Lang);
        }
    }

    //render
    render() {
        //i18next.changeLanguage(this.state.Lang);
        return (
            <div className="sidebar row col-6">
                <div className="sidebar-wrapper">
                    <ul className="nav">
                        <li>
                            <a href="/"><h4>{i18next.t('Home')}</h4></a>
                        </li>
                        <li>
                            <a onClick={() => this.translate("eng")}><h4>English</h4></a>
                        </li>
                        <li>
                            <a onClick={() => this.translate("cree")}><h4>Cree</h4></a>
                        </li>
                        <li>
                            <a onClick={() => this.translate("syllabic")}><h4>Syllabic</h4></a>
                        </li>
                    </ul>
                </div>
            </div>
        );
    }

}

export default NavSideBar;