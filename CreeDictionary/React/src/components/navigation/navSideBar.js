import React from 'react';

import i18next from '../../utils/translate';

class NavSideBar extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            Lang: "en",
        };
    }

    translate(lan){
        if (lan === "cree"){
            this.setState({
                Lang: "cree"
            })
        }else if (lan === "syllabic"){
            this.setState({
                Lang: "syllabic"
            })
        }else{
            this.setState({
                Lang: "en"
            })
        }
    }

    componentDidUpdate(prevProps) {
        // Typical usage (don't forget to compare props):
        if (prevProps === null) {
            alert('its dif');
            //this.gainList();
        }
    }
    
    //render
    render() {
        //i18next.changeLanguage(this.state.Lang);
        return (
            <div className="sidebar">
            <div className="sidebar-wrapper">
                <section className="nav">
                    <li>
                        <a href="/">{i18next.t('BackToTheTop')}</a>
                    </li>
                    <li>
                        <a onClick={() => this.translate("cree")}>Cree</a>
                    </li>
                    <li>
                        <a onClick={() => this.translate("eng")}>English</a>
                    </li>
                    <li>
                        <a onClick={() => this.translate("syllabic")}>Syllabic</a>
                    </li>
                </section>
            </div>
            </div>
        );
    }

}

export default NavSideBar;