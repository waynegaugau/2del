import { useEffect, useReducer } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Container } from "react-bootstrap";
import { Toaster } from "react-hot-toast";
import cookie from "react-cookies";

import { MyDipatcherContext, MyUserContext } from "./configs/MyContexts";
import MyUserReducer from "./reducers/MyUserReducer";

import Header from "./component/layout/Header";
import Footer from "./component/layout/Footer";
import MyToaster from "./component/layout/MyToaster";

import Home from "./pages/public/Home";
import Register from "./pages/public/Register";
import Login from "./pages/public/Login";
import Pet from "./pages/owner/Pet";
import Booking from "./pages/owner/Booking";
import MyAppointments from "./pages/owner/MyAppointments";
import PaymentCheckout from "./pages/owner/PaymentCheckout";
import PaymentResult from "./pages/owner/PaymentResult";
import PetMedicalHistory from "./pages/owner/PetMedicalHistory";
import StaffAppointmentList from "./pages/staff/StaffAppointmentList";
import MedicineManagement from "./pages/staff/MedicineManagement";
import StaffPetList from "./pages/staff/StaffPetList";
import AdminClinic from "./pages/admin/AdminClinic";
import AdminReports from "./pages/admin/AdminReports";
import AdminStaff from "./pages/admin/AdminStaff";
import AdminService from "./pages/admin/AdminService";

import "./App.css";

const App = () => {
  const [user, dispatch] = useReducer(MyUserReducer, cookie.load("user") || null);

  useEffect(() => {
    // Firebase notification setup can be re-enabled here when the config is available.
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
              {/* Public */}
              <Route path="/" element={<Home />} />
              <Route path="/register" element={<Register />} />
              <Route path="/login" element={<Login />} />

              {/* Owner */}
              <Route path="/pets" element={<Pet />} />
              <Route path="/my-pets" element={<Pet />} />
              <Route path="/my-pets/:petId/history" element={<PetMedicalHistory />} />
              <Route path="/booking" element={<Booking />} />
              <Route path="/appointments" element={<MyAppointments />} />
              <Route path="/payments/:paymentId/checkout" element={<PaymentCheckout />} />
              <Route path="/payment-result" element={<PaymentResult />} />

              {/* Staff */}
              <Route path="/staff/appointments" element={<StaffAppointmentList />} />
              <Route path="/staff/pets" element={<StaffPetList />} />
              <Route path="/staff/pets/:petId/history" element={<PetMedicalHistory />} />
              <Route path="/staff/medicines" element={<MedicineManagement />} />

              {/* Admin */}
              <Route path="/admin/reports" element={<AdminReports />} />
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
