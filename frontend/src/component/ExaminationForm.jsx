import React, { useState } from "react";
import { Modal, Form, Button, Row, Col, Alert } from "react-bootstrap";
import { authApis, endpoint } from "../configs/Apis";
import toast from "react-hot-toast";

const ExaminationForm = ({ appointment, show, onHide, onComplete }) => {
    const [step, setStep] = useState(1); // 1: Bệnh án, 2: Đơn thuốc
    const [recordId, setRecordId] = useState(null);
    const [loading, setLoading] = useState(false);
    
    // State cho Hồ sơ bệnh án[cite: 15, 23]
    const [recordData, setRecordData] = useState({
        symptoms: "",
        diagnosis: "",
        treatment: "",
        note: ""
    });

    // 1. Lưu Hồ sơ bệnh án[cite: 8, 23]
    const handleSubmitRecord = async (e) => {
        e.preventDefault();
        try {
            setLoading(true);
            const res = await authApis().post(endpoint['appointment_medical_record'](appointment.id), recordData);
            const newRecord = res.data.data || res.data;
            setRecordId(newRecord.id);
            toast.success("Đã lưu hồ sơ bệnh án!");
            setStep(2); // Chuyển sang bước kê đơn
        } catch (ex) {
            toast.error(ex.response?.data?.message || "Lỗi khi lưu hồ sơ.");
        } finally {
            setLoading(false);
        }
    };

    // 2. Kết thúc ca khám
    const handleFinishAll = async () => {
        try {
            await authApis().post(endpoint['appointment_complete'](appointment.id));
            toast.success("Ca khám đã hoàn tất!");
            onComplete(); // Tải lại danh sách ở trang cha
            onHide();
        } catch (ex) {
            toast.error("Lỗi khi kết thúc ca khám.");
        }
    };

    return (
        <Modal show={show} onHide={onHide} size="lg" backdrop="static">
            <Modal.Header closeButton>
                <Modal.Title>
                    {step === 1 ? `Khám bệnh: ${appointment.pet_name}` : "Kê đơn thuốc"}
                </Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {step === 1 ? (
                    <Form onSubmit={handleSubmitRecord}>
                        <Form.Group className="mb-3">
                            <Form.Label className="fw-bold">Triệu chứng[cite: 11, 15]</Form.Label>
                            <Form.Control as="textarea" rows={2} required 
                                onChange={e => setRecordData({...recordData, symptoms: e.target.value})} />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label className="fw-bold">Chẩn đoán[cite: 11, 15]</Form.Label>
                            <Form.Control as="textarea" rows={2} required 
                                onChange={e => setRecordData({...recordData, diagnosis: e.target.value})} />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label className="fw-bold">Hướng điều trị[cite: 11, 15]</Form.Label>
                            <Form.Control as="textarea" rows={2} 
                                onChange={e => setRecordData({...recordData, treatment: e.target.value})} />
                        </Form.Group>
                        <Button variant="primary" type="submit" className="w-100" disabled={loading}>
                            {loading ? "Đang lưu..." : "Lưu hồ sơ & Chuyển sang kê đơn"}
                        </Button>
                    </Form>
                ) : (
                    <div className="text-center p-4">
                        <Alert variant="success">Hồ sơ bệnh án đã được tạo thành công!</Alert>
                        <p>Bạn có muốn tiếp tục kê đơn thuốc cho bé không?</p>
                        <div className="d-flex justify-content-center gap-3">
                            <Button variant="outline-primary" onClick={() => {/* Dẫn tới logic kê đơn chi tiết */}}>
                                + Thêm đơn thuốc[cite: 22]
                            </Button>
                            <Button variant="success" onClick={handleFinishAll}>
                                Hoàn tất & Đóng ca khám
                            </Button>
                        </div>
                    </div>
                )}
            </Modal.Body>
        </Modal>
    );
};

export default ExaminationForm;