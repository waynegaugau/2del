import { useEffect, useReducer } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Container } from "react-bootstrap";
import toast, { Toaster } from "react-hot-toast";
import cookie from "react-cookies";

// Contexts & Reducers
import { MyDipatcherContext, MyUserContext } from "./configs/MyContexts";
import MyUserReducer from "./reducers/MyUserReducer";

// Firebase (Tạm ẩn chờ bạn cung cấp file config)
// import { generateToken, messaging } from './notifications/firebase';
// import { onMessage } from 'firebase/messaging';

// Layout Components
import Header from "./component/layout/Header";
import Footer from "./component/layout/Footer";
import MyToaster from "./component/layout/MyToaster";

// Pages
import Home from "./component/Home";
// import Register from "./component/Register";
// import Login from "./component/Login";
// import DoctorAvailability from "./component/bookDoctor/DoctorAvailability";
// import AppointmentUpdate from "./component/bookDoctor/AppointmentUpdate";
// import Appointment from "./component/bookDoctor/Appointment";
// import Calendar from "./component/findDoctor/Calendar";
// import Booking from "./component/bookDoctor/Booking";
// import PaymentMethod from "./component/PaymentMethod";
// import PaymentReturn from "./component/PaymentReturn";
// import Invoice from "./component/Invoice";
// import EditProfile from "./component/EditProfile";
// import ChangePassword from "./component/ChangePassword";
// import SpecialtyList from "./component/bookDoctor/SpecialtyList";
// import MedicineManagement from "./component/MedicineManagement";

import "./App.css";

const App = () => {
  const [user, dispatch] = useReducer(MyUserReducer, cookie.load("user") || null);

  useEffect(() => {
    // Đoạn này sẽ mở lại khi có file firebase
    /*
    generateToken();
    onMessage(messaging, (payload) => {
      console.log(payload);
      toast(payload.notification.body);
    });
    */
  }, []);

  return (
    <MyUserContext.Provider value={user}>
      <MyDipatcherContext.Provider value={dispatch}>
        <BrowserRouter>
          <Header />
          <Container fluid>
            <MyToaster />
            {/* Component Toaster của react-hot-toast để hiển thị thông báo */}
            <Toaster position="top-right" /> 
            <Routes>
              <Route path="/" element={<Home />} />
              {/* <Route path="/doctorAvailability" element={<DoctorAvailability />} />
              <Route path="/updateAppointment" element={<AppointmentUpdate />} />
              <Route path="/appointment" element={<Appointment />} />
              <Route path="/calendar" element={<Calendar />} />
              <Route path="/booking" element={<Booking />} />
              <Route path="/register" element={<Register />} />
              <Route path="/login" element={<Login />} />
              <Route path="/payment-method" element={<PaymentMethod />} />
              <Route path="/payment-return" element={<PaymentReturn />} />
              <Route path="/invoice" element={<Invoice />} />
              <Route path="/editProfile" element={<EditProfile />} />
              <Route path="/change-password" element={<ChangePassword />} />
              <Route path="/select-specialty" element={<SpecialtyList />} />
              <Route path="/medicine-management" element={<MedicineManagement />} /> */}
            </Routes>
          </Container>
          <Footer />
        </BrowserRouter>
      </MyDipatcherContext.Provider>
    </MyUserContext.Provider>
  );
};

export default App;