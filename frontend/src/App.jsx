import './App.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Header from './component/layout/Header';
import Footer from './component/layout/Footer';
import MyToaster from './component/layout/MyToaster';
import Home from './component/Home';
import Register from './component/Register';
import Login from './component/Login';
import { Container } from 'react-bootstrap';
import toast, { Toaster } from "react-hot-toast"
import { createContext, useEffect, useReducer } from "react"
import cookie from 'react-cookies'
import { useState } from 'react';


const App = () => {

  const [user, dispatch] = useReducer(MyUserReducer, cookie.load('user') || null);
  useEffect(() => {
    generateToken();
    onMessage(messaging, (payload) => {
      console.log(payload);
      toast(payload.notification.body);
    })
  }
    , [])
  return (

    <MyUserContext.Provider value={user}>
      <MyDipatcherContext.Provider value={dispatch}>
        <BrowserRouter>
          <Header />
          <Container fluid >
            <MyToaster />
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/booking" element={<Booking />} />
              <Route path="/register" element={<Register />} />
              <Route path="/login" element={<Login />} />
            </Routes>
          </Container>
          <Footer />
        </BrowserRouter>
      </MyDipatcherContext.Provider>
    </MyUserContext.Provider>


  )
}

export default App;
