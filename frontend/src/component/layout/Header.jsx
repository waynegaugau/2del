import { Navbar, Nav, Container } from "react-bootstrap";
import { NavLink } from "react-router-dom";
import "./styles/Header.css"; 

const Header = () => {
    return (
        <Navbar bg="dark" variant="dark" expand="lg" className="py-3 shadow-sm">
            <Container>
                {/* Logo / Tên thương hiệu */}
                <Navbar.Brand as={NavLink} to="/" className="fw-bold fs-4 me-5">
                    THÚ Y 2DEL
                </Navbar.Brand>

                {/* Nút toggle cho giao diện điện thoại */}
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                
                <Navbar.Collapse id="basic-navbar-nav">
                    {/* Các link điều hướng chính */}
                    <Nav className="me-auto custom-nav">
                        <Nav.Link as={NavLink} to="/gioi-thieu" className="mx-2 fw-semibold">
                            Giới thiệu
                        </Nav.Link>
                        <Nav.Link as={NavLink} to="/dich-vu" className="mx-2 fw-semibold">
                            Dịch vụ
                        </Nav.Link>
                        <Nav.Link as={NavLink} to="/dat-lich" className="mx-2 fw-semibold">
                            Đặt lịch
                        </Nav.Link>
                    </Nav>

                    {/* Link đăng nhập góc phải */}
                    <Nav>
                        <Nav.Link as={NavLink} to="/login" className="fw-bold text-white">
                            Đăng nhập
                        </Nav.Link>
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default Header;