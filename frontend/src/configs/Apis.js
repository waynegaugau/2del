import axios from "axios";
import cookie from 'react-cookies';

// Địa chỉ Backend Django của bạn
const BASE_URL = 'http://127.0.0.1:8000/api/';

export const endpoint = {
    // Auth
    'register': '/auth/register/',
    'login': '/auth/login/',
    'refresh': '/auth/refresh/',
    'logout': '/auth/logout/',
    'current_user': '/auth/profile/',
    
    // Pets
    'pets': '/pets/',
    'pet_detail': (petId) => `/pets/${petId}/`,
    
    // Clinics & Services
    'clinics': '/clinics/',
    'services': '/services/',
    'services_by_clinic': (clinicId) => `/clinics/${clinicId}/services/`,
    
    // Appointments
    'appointments': '/appointments/',
    'appointment_detail': (appId) => `/appointments/${appId}/`,
    'appointment_confirm': (appId) => `/appointments/${appId}/confirm/`,
    
    // Medicines & Prescriptions
    'medicines': '/medicines/',
    'prescriptions_by_record': (recordId) => `/medical-records/${recordId}/prescription/`,
    
    // Medical Records
    'medical_records_by_pet': (petId) => `/pets/${petId}/medical-records/`,
};

// Instance cho các request công khai (Login, Register)
export default axios.create({
    baseURL: BASE_URL
});

// Instance cho các request cần đăng nhập (Có gắn Token)
export const authApis = () => {
    return axios.create({
        baseURL: BASE_URL,
        headers: {
            'Authorization': `Bearer ${cookie.load('token')}`
        }
    });
};

// Instance cho upload file (Ảnh đại diện, ảnh thú cưng)
export const authFormDataApis = () => {
    return axios.create({
        baseURL: BASE_URL,
        headers: {
            'Authorization': `Bearer ${cookie.load('token')}`,
            'Content-Type': 'multipart/form-data'
        }
    });
};