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
import Register from "./component/Register";
import Login from "./component/Login";
import Pet from "./component/Pet";
import Booking from "./component/Booking";
import MyAppointments from "./component/MyAppointments";
import StaffAppointmentList from "./component/StaffAppointmentList";
import PetMedicalHistory from "./component/PetMedicalHistory";
import MedicineManagement from "./component/MedicineManagement";
import StaffPetList from "./component/StaffPetList";
import AdminClinic from "./component/pages/admin/AdminClinic";
import AdminStaff from "./component/pages/admin/AdminStaff";
import AdminService from "./component/pages/admin/AdminService";
// import DoctorAvailability from "./component/bookDoctor/DoctorAvailability";
// import AppointmentUpdate from "./component/bookDoctor/AppointmentUpdate";
// import Appointment from "./component/bookDoctor/Appointment";
// import Calendar from "./component/findDoctor/Calendar";
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
          <Container fluid className="p-0">
            <MyToaster />
            <Toaster position="top-right" />
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/register" element={<Register />} />
              <Route path="/login" element={<Login />} />
              <Route path="/pets" element={<Pet />} />
              <Route path="/booking" element={<Booking />} />
              <Route path="/appointments" element={<MyAppointments />} />
              <Route path="/staff/appointments" element={<StaffAppointmentList />} />
              <Route path="/staff/pets/:petId/history" element={<PetMedicalHistory />} />
              <Route path="/my-pets/:petId/history" element={<PetMedicalHistory isOwner={true} />} />
              <Route path="/staff/medicines" element={<MedicineManagement />} />
              {/* Route dành cho Staff */}
              <Route path="/staff/pets/:petId/history" element={<PetMedicalHistory isOwnerPath={false} />} />

              {/* Route dành cho Chủ nuôi */}
              <Route path="/my-pets/:petId/history" element={<PetMedicalHistory isOwnerPath={true} />} />
              {/* Dành cho Staff */}
              <Route path="/staff/pets" element={<StaffPetList />} />
              <Route path="/staff/pets/:petId/history" element={<PetMedicalHistory />} />

              {/* Dành cho Owner */}
              <Route path="/my-pets" element={<Pet />} />
              <Route path="/my-pets/:petId/history" element={<PetMedicalHistory />} />

              {/* Chỉ dành cho ADMIN */}
              <Route path="/admin/clinics" element={<AdminClinic />} />
              <Route path="/admin/staffs" element={<AdminStaff />} />
              <Route path="/admin/services" element={<AdminService />} />
            </Routes>
          </Container>
          <Footer />
        </BrowserRouter>
      </MyDipatcherContext.Provider>
    </MyUserContext.Provider>
  );
};

export default App;