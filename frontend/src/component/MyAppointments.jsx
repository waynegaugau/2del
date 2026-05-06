import React, { useEffect, useState } from "react";
import { Container, Table, Badge, Spinner, Tab, Tabs, Card, Button } from "react-bootstrap";
import { authApis, endpoint } from "../configs/Apis";
import toast from "react-hot-toast";
import moment from "moment"; // Nên cài moment để định dạng ngày tháng

const MyAppointments = () => {
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);

    // 1. Load danh sách lịch hẹn[cite: 10, 11]
    const loadAppointments = async () => {
        try {
            setLoading(true);
            const res = await authApis().get(endpoint['appointments']);
            // Backend trả về mảng lịch hẹn của user hiện tại[cite: 7, 11]
            setAppointments(res.data.data || res.data);
        } catch (ex) {
            toast.error("Không thể tải danh sách lịch hẹn.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadAppointments();
    }, []);

    // 2. Hàm hỗ trợ hiển thị màu sắc trạng thái
    const getStatusBadge = (status) => {
        switch (status) {
            case "PENDING": return <Badge bg="warning" text="dark">Chờ xác nhận</Badge>;
            case "CONFIRMED": return <Badge bg="success">Đã xác nhận</Badge>;
            case "CHECKED_IN": return <Badge bg="info">Đã đến phòng khám</Badge>;
            case "IN_PROGRESS": return <Badge bg="primary">Đang khám</Badge>;
            case "COMPLETED": return <Badge bg="secondary">Hoàn thành</Badge>;
            case "CANCELLED": return <Badge bg="danger">Đã hủy</Badge>;
            case "NO_SHOW": return <Badge bg="dark">Vắng mặt</Badge>;
            default: return <Badge bg="light" text="dark">{status}</Badge>;
        }
    };

    // 3. Logic Hủy lịch (Chỉ cho phép khi đang PENDING)
    const handleCancel = async (appId) => {
        if (window.confirm("Bạn có chắc chắn muốn hủy lịch hẹn này?")) {
            try {
                // Sử dụng hàm cancel_appointment của Backend[cite: 10, 11]
                await authApis().delete(endpoint['appointment_detail'](appId));
                toast.success("Đã hủy lịch hẹn.");
                loadAppointments(); // Tải lại danh sách
            } catch (ex) {
                toast.error(ex.response?.data?.message || "Không thể hủy lịch.");
            }
        }
    };

    const renderTable = (data) => (
        <Table responsive hover className="mt-3 align-middle">
            <thead className="table-light">
                <tr>
                    <th>Thú cưng</th>
                    <th>Phòng khám</th>
                    <th>Dịch vụ</th>
                    <th>Thời gian</th>
                    <th>Trạng thái</th>
                    <th>Hành động</th>
                </tr>
            </thead>
            <tbody>
                {data.map((app) => (
                    <tr key={app.id}>
                        <td className="fw-bold">{app.pet_name}</td>
                        <td>{app.clinic_name}</td>
                        <td>{app.service_name}</td>
                        <td>{moment(app.appointment_time).format("DD/MM/YYYY HH:mm")}</td>
                        <td>{getStatusBadge(app.status)}</td>
                        <td>
                            {/* Chỉ cho phép hủy nếu lịch đang PENDING[cite: 10] */}
                            {app.status === "PENDING" && (
                                <Button variant="outline-danger" size="sm" onClick={() => handleCancel(app.id)}>
                                    Hủy
                                </Button>
                            )}
                            {app.status === "COMPLETED" && (
                                <Button variant="outline-primary" size="sm">Xem hồ sơ</Button>
                            )}
                        </td>
                    </tr>
                ))}
            </tbody>
        </Table>
    );

    if (loading) return <Container className="text-center mt-5"><Spinner animation="border" variant="success" /></Container>;

    return (
        <Container className="mt-4 mb-5">
            <h2 className="mb-4 text-success fw-bold">LỊCH HẸN CỦA TÔI</h2>
            
            <Tabs defaultActiveKey="all" className="mb-3 custom-tabs">
                <Tab eventKey="all" title="Tất cả">
                    {renderTable(appointments)}
                </Tab>
                <Tab eventKey="upcoming" title="Sắp tới">
                    {renderTable(appointments.filter(app => ["PENDING", "CONFIRMED"].includes(app.status)))}
                </Tab>
                <Tab eventKey="finished" title="Đã xong/Hủy">
                    {renderTable(appointments.filter(app => ["COMPLETED", "CANCELLED", "NO_SHOW"].includes(app.status)))}
                </Tab>
            </Tabs>

            {appointments.length === 0 && (
                <Card className="text-center p-5 border-0 bg-light">
                    <p className="text-muted">Bạn chưa có lịch hẹn nào.</p>
                </Card>
            )}
        </Container>
    );
};

export default MyAppointments;