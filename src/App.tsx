import React from "react";
import {
    HashRouter as Router,
    Route,
    Routes,
    Navigate,
} from "react-router-dom";

import NavBar from "./components/Navbar";

import Home from "./pages/Home";
import Download from "./pages/Download";
import Introduction from "./pages/Introduction";
import MultilineCommand from "./pages/MultilineCommand";
import Basics from "./pages/Basics";
import Advanced from "./pages/Advanced";
import Submitted from "./pages/Submitted";

function App() {
    return (
        <Router>
            <div className="App w-screen">
                <NavBar />
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/download" element={<Download />} />
                    <Route
                        path="/getting-started/introduction"
                        element={<Introduction />}
                    />
                    <Route
                        path="/getting-started/how-it-works"
                        element={<Introduction />}
                    />
                    <Route
                        path="/getting-started/installation"
                        element={<Introduction />}
                    />
                    <Route
                        path="/getting-started/code"
                        element={<Introduction />}
                    />
                    <Route
                        path="/documentation/multiline-command"
                        element={<MultilineCommand />}
                    />
                    <Route path="/examples/basics" element={<Basics />} />
                    <Route path="/examples/advanced" element={<Advanced />} />
                    <Route path="/examples/submitted" element={<Submitted />} />
                    <Route path="/*" element={<Navigate to="/" />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
