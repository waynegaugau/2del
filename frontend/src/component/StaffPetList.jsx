import React, { useEffect, useState } from "react";
import { Container, Table, Button, Spinner, InputGroup, Form } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { authApis, endpoint } from "../configs/Apis";
import toast from "react-hot-toast";

const StaffPetList = () => {
    const [pets, setPets] = useState([]);
    const [q, setQ] = useState("");
    const [loading, setLoading] = useState(false); // THÊM DÒNG NÀY
    const navigate = useNavigate();

    const loadPets = async () => {
        try {
            setLoading(true);
            // Gửi params 'q' để Backend lọc theo tên pet/chủ nuôi
            const res = await authApis().get(endpoint['pets'], {
                params: { q: q } 
            });

            const data = res.data.data || res.data;
            setPets(Array.isArray(data) ? data : []);
        } catch (ex) {
            console.error("Lỗi tải danh sách pet:", ex);
            // toast.error("Không thể tải danh sách thú cưng.");
        } finally {
            setLoading(false);
        }
    };

    // THÊM ĐOẠN NÀY: Gọi lại hàm loadPets mỗi khi từ khóa 'q' thay đổi
    useEffect(() => {
        const timer = setTimeout(() => {
            loadPets();
        }, 500); // Debounce 500ms để tránh gọi API liên tục khi gõ phím

        return () => clearTimeout(timer);
    }, [q]);

    if (loading && pets.length === 0) return <div className="text-center mt-5"><Spinner animation="border" /></div>;

    return (
        <Container className="mt-4">
            <h2 className="text-primary fw-bold mb-4">DANH SÁCH THÚ CƯNG HỆ THỐNG</h2>
            <Form.Control
                placeholder="Tìm tên Pet hoặc Chủ nuôi..."
                className="mb-3"
                onChange={(e) => setQ(e.target.value)}
            />
            <Table striped bordered hover>
                <thead>
                    <tr>
                        <th>Tên Pet</th>
                        <th>Chủ nuôi</th>
                        <th>Loài</th>
                        <th>Thao tác</th>
                    </tr>
                </thead>
                <tbody>
                    {pets.map(p => (
                        <tr key={p.id}>
                            <td>{p.name}</td>
                            <td>{p.owner_name}</td>
                            <td>{p.species}</td>
                            <td>
                                <Button
                                    variant="info"
                                    size="sm"
                                    onClick={() => navigate(`/staff/pets/${p.id}/history`)} // Path Staff
                                >
                                    Lịch sử bệnh án
                                </Button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </Table>
        </Container>
    );
};

export default StaffPetList;