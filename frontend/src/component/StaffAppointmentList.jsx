import React, { useEffect, useState } from "react";
import { Container, Table, Button, Badge, Spinner, Card } from "react-bootstrap";
import { authApis, endpoint } from "../configs/Apis";
import toast from "react-hot-toast";
import moment from "moment";
import ExaminationForm from "./ExaminationForm"; // Đảm bảo bạn đã tạo file này

const StaffAppointmentList = () => {
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);
    
    // 1. Đưa State vào bên trong Component
    const [selectedApp, setSelectedApp] = useState(null);
    const [showExam, setShowExam] = useState(false);

    const loadAppointments = async () => {
        try {
            setLoading(true);
            const res = await authApis().get(endpoint['staff_clinic_appointments']);
            setAppointments(res.data.data || res.data);
        } catch (ex) {
            toast.error("Không thể tải danh sách lịch hẹn của phòng khám.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadAppointments();
    }, []);

    const updateStatus = async (id, actionEndpoint, successMsg) => {
        try {
            await authApis().post(actionEndpoint(id));
            toast.success(successMsg);
            loadAppointments(); 
        } catch (ex) {
            toast.error(ex.response?.data?.message || "Thao tác thất bại");
        }
    };

    const getStatusBadge = (status) => {
        const statusMap = {
            "PENDING": { bg: "warning", text: "Chờ duyệt" },
            "CONFIRMED": { bg: "success", text: "Đã xác nhận" },
            "CHECKED_IN": { bg: "info", text: "Đã đến" },
            "IN_PROGRESS": { bg: "primary", text: "Đang khám" },
            "COMPLETED": { bg: "secondary", text: "Hoàn thành" },
            "CANCELLED": { bg: "danger", text: "Đã hủy" }
        };
        const s = statusMap[status] || { bg: "light", text: status };
        return <Badge bg={s.bg}>{s.text}</Badge>;
    };

    if (loading) return <Container className="text-center mt-5"><Spinner animation="border" /></Container>;

    return (
        <Container className="mt-4">
            <h2 className="mb-4 fw-bold text-primary">QUẢN LÝ LỊCH HẸN PHÒNG KHÁM</h2>
            <Card className="shadow-sm border-0">
                <Table responsive hover className="mb-0 align-middle">
                    <thead className="table-primary">
                        <tr>
                            <th>Khách hàng</th>
                            <th>Thú cưng</th>
                            <th>Dịch vụ</th>
                            <th>Thời gian</th>
                            <th>Trạng thái</th>
                            <th>Thao tác</th>
                        </tr>
                    </thead>
                    <tbody>
                        {appointments.map(app => (
                            <tr key={app.id}>
                                <td>{app.owner_username}</td>
                                <td>{app.pet_name}</td>
                                <td>{app.service_name}</td>
                                <td>{moment(app.appointment_time).format("DD/MM HH:mm")}</td>
                                <td>{getStatusBadge(app.status)}</td>
                                <td>
                                    {app.status === "PENDING" && (
                                        <Button size="sm" variant="success" className="me-2"
                                            onClick={() => updateStatus(app.id, endpoint['appointment_confirm'], "Đã xác nhận lịch")}>
                                            Xác nhận
                                        </Button>
                                    )}

                                    {app.status === "CONFIRMED" && (
                                        <Button size="sm" variant="info" className="me-2 text-white"
                                            onClick={() => updateStatus(app.id, endpoint['appointment_check_in'], "Đã check-in")}>
                                            Tiếp đón
                                        </Button>
                                    )}

                                    {app.status === "CHECKED_IN" && (
                                        <Button size="sm" variant="primary"
                                            onClick={() => updateStatus(app.id, endpoint['appointment_start'], "Bắt đầu ca khám")}>
                                            Bắt đầu khám
                                        </Button>
                                    )}

                                    {/* 2. Cập nhật sự kiện onClick để mở Modal[cite: 24] */}
                                    {app.status === "IN_PROGRESS" && (
                                        <Button size="sm" variant="outline-primary" onClick={() => {
                                            setSelectedApp(app);
                                            setShowExam(true);
                                        }}>
                                            Nhập kết quả
                                        </Button>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </Table>
            </Card>

            {/* 3. Thêm Component Modal vào cuối[cite: 24] */}
            {selectedApp && (
                <ExaminationForm 
                    appointment={selectedApp} 
                    show={showExam} 
                    onHide={() => setShowExam(false)}
                    onComplete={loadAppointments} 
                />
            )}
        </Container>
    );
};

export default StaffAppointmentList;