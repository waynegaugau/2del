import { useContext } from 'react';
import { Navbar, Nav, Container, NavDropdown } from 'react-bootstrap';
import { NavLink, useNavigate } from 'react-router-dom';
import { MyUserContext, MyDipatcherContext } from '../../configs/MyContexts';
import './styles/Header.css';

const Header = () => {
    const user = useContext(MyUserContext);
    const dispatch = useContext(MyDipatcherContext);
    const nav = useNavigate();

    const logout = () => {
        dispatch({ type: "logout" });
        nav("/login");
    };

    return (
        <Navbar bg="dark" variant="dark" expand="lg" className="py-3 shadow-sm sticky-top">
            <Container>
                <Navbar.Brand as={NavLink} to="/" className="fw-bold fs-4 me-5">
                    THÚ Y 2DEL
                </Navbar.Brand>

                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto custom-nav">
                        <Nav.Link as={NavLink} to="/" className="mx-2 fw-semibold">Trang chủ</Nav.Link>
                        <Nav.Link as={NavLink} to="/dat-lich" className="mx-2 fw-semibold">Đặt lịch</Nav.Link>
                        <Nav.Link as={NavLink} to="/medicine-management" className="mx-2 fw-semibold">Kho thuốc</Nav.Link>
                    </Nav>

                    <Nav className="align-items-center">
                        {user === null ? (
                            <>
                                <Nav.Link as={NavLink} to="/login" className="fw-bold text-white mx-2">
                                    Đăng nhập
                                </Nav.Link>
                                <Nav.Link as={NavLink} to="/register" className="btn btn-outline-success text-white px-3 fw-bold">
                                    Đăng ký
                                </Nav.Link>
                            </>
                        ) : (
                            <NavDropdown 
                                title={<span className="fw-bold text-success">Chào, {user.first_name || user.username}</span>} 
                                id="user-dropdown"
                                align="end"
                            >
                                <NavDropdown.Item as={NavLink} to="/editProfile">Hồ sơ cá nhân</NavDropdown.Item>
                                <NavDropdown.Item as={NavLink} to="/change-password">Đổi mật khẩu</NavDropdown.Item>
                                <NavDropdown.Divider />
                                <NavDropdown.Item onClick={logout} className="text-danger fw-bold">
                                    Đăng xuất
                                </NavDropdown.Item>
                            </NavDropdown>
                        )}
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default Header;