import { useContext, useState, useEffect } from "react";
import { Alert, Button, Col, Container, FloatingLabel, Form, Row } from "react-bootstrap";
import { useNavigate, useLocation } from "react-router-dom";
import cookie from 'react-cookies';
import toast from "react-hot-toast";

import Apis, { authApis, endpoint } from "../configs/Apis";
import { MyDipatcherContext } from "../configs/MyContexts";
import MySpinner from "./layout/MySpinner";
import "./styles/Login.css";

const Login = () => {
    const [user, setUser] = useState({});
    const [loading, setLoading] = useState(false);
    const [msg, setMsg] = useState();

    const dispatch = useContext(MyDipatcherContext);
    const nav = useNavigate();
    const location = useLocation();
    const [message, setMessage] = useState(location.state?.message || "");

    useEffect(() => {
        if (message) {
            const timer = setTimeout(() => setMessage(""), 5000);
            return () => clearTimeout(timer);
        }
    }, [message]);

    const info = [
        { label: "Tên đăng nhập", field: "username", type: "text" },
        { label: "Mật khẩu", field: "password", type: "password" },
    ];

    const setState = (value, field) => {
        setUser({ ...user, [field]: value });
    };

    const login = async (e) => {
        e.preventDefault();
        try {
            setLoading(true);
            setMsg(null);

            const res = await Apis.post(endpoint['login'], { ...user });

            // TRUY CẬP ĐÚNG CẤU TRÚC: res.data.data.access_token
            const accessToken = res.data?.data?.access_token;
            const userData = res.data?.data?.user;

            if (accessToken) {
                // 1. Lưu token vào cookie
                cookie.save('token', accessToken, { path: '/' });

                // 2. Vì server đã trả về object 'user' luôn rồi, 
                // bạn có thể dùng luôn mà không cần gọi lại API profile (tiết kiệm 1 request)
                cookie.save('user', userData, { path: '/' });

                dispatch({
                    "type": "login",
                    "payload": userData
                });

                toast.success("Đăng nhập thành công!");
                nav("/");
            } else {
                console.error("Cấu trúc JSON thực tế:", res.data);
                setMsg("Không tìm thấy access_token trong phản hồi từ server.");
            }
        } catch (ex) {
            console.error("Lỗi đăng nhập:", ex);
            const errorMsg = ex.response?.data?.message || "Tên đăng nhập hoặc mật khẩu không chính xác.";
            setMsg(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container fluid className="p-0">
            {message && <div className="fade-out-message">{message}</div>}
            <Row className="justify-content-center custom-row-primary mt-4">
                <Col lg={5} md={7} sm={10} className="p-4 shadow rounded bg-white">
                    <h1 className="text-center text-success mb-4 fw-bold">ĐĂNG NHẬP</h1>
                    {msg && <Alert variant="danger">{msg}</Alert>}
                    <Form onSubmit={login}>
                        {info.map(f => (
                            <FloatingLabel key={f.field} controlId={`floating-${f.field}`} label={f.label} className="mb-3">
                                <Form.Control
                                    type={f.type}
                                    placeholder={f.label}
                                    required
                                    value={user[f.field] || ""}
                                    onChange={e => setState(e.target.value, f.field)}
                                />
                            </FloatingLabel>
                        ))}

                        <Button type="submit" variant="success" className="w-100 py-2 fw-bold" disabled={loading}>
                            {loading ? <MySpinner /> : "Đăng nhập"}
                        </Button>
                    </Form>

                    <div className="mt-4 text-center border-top pt-3">
                        <p className="mb-0 text-muted">Chưa có tài khoản?</p>
                        <Button
                            variant="link"
                            className="text-success fw-bold p-0"
                            onClick={() => nav("/register")}
                        >
                            Đăng ký ngay tại đây
                        </Button>
                    </div>
                </Col>
            </Row>
        </Container>
    );
};

export default Login;