import { Col, Container, Row } from "react-bootstrap";
// Nhớ tạo thư mục 'styles' (viết thường) bên trong thư mục 'layout' nhé
import "./styles/Footer.css";

const Footer = () => {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="site-footer mt-5">
            <Container className="p-2">
                <hr />
                <Row>
                    <Col className="text-center footer-bottom">
                        <p className="small">Copyright © {currentYear} - eDOCTOR.</p>
                    </Col>
                </Row>
                <hr />
            </Container>
        </footer>
    );
};

export default Footer;