import Header from "./Header";
import Footer from "./Footer";
import { Component } from "react";

class Layout extends Component {
  render() {
    return (
      <div className="App">
        <Header></Header>
        <main className="app__content app__pane">{this.props.children}</main>
        <Footer></Footer>
      </div>
    );
  }
}

export default Layout;
