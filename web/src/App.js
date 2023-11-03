import React from 'react';
import {BrowserRouter as Router, Route, Routes, Link} from 'react-router-dom';
import {Container, Navbar, Nav, NavLink} from 'react-bootstrap';
import Lesk from './pages/Lesk';
import Analytics from './pages/Analytics';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
    document.title = 'Word Sense Disambiguation GUI';

    return (
        <Router>
            <Navbar bg="light" expand="lg">
                <Container>
                    <Navbar.Brand as={Link} to="/">Word Sense Disambiguation</Navbar.Brand>
                    <Navbar.Toggle aria-controls="basic-navbar-nav"/>
                    <Navbar.Collapse id="basic-navbar-nav">
                        <Nav className="ms-auto"> {/* This class will align nav items to the right */}
                            <Nav.Link as={Link} to="/">Lesk</Nav.Link>
                            {/*<Nav.Link as={Link} to="/analytics">Analytics</Nav.Link>*/}
                        </Nav>
                    </Navbar.Collapse>
                </Container>
            </Navbar>

            <Container style={{paddingTop: '1rem'}}>
                <Routes>
                    <Route path="/analytics" element={<Analytics/>}/>
                    <Route path="/" element={<Lesk/>}/>
                </Routes>
            </Container>
        </Router>
    );
}

export default App;