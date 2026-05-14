# Test Report

## 1. Thông tin chung

| Mục | Nội dung |
|---|---|
| Dự án | Hệ thống quản lý phòng khám thú y 2DEL |
| Tài liệu liên quan | `docs/test-plan.md`, `docs/requirements.md`, `docs/api-docs.md` |
| Ngày kiểm thử | 15/05/2026 |
| Người thực hiện | Nhóm 2DEL |
| Môi trường | Windows, Python 3.13, Django 6.0.3, Django REST Framework, React 19 |

## 2. Mục tiêu kiểm thử

Đợt kiểm thử nhằm xác nhận các chức năng chính của hệ thống hoạt động đúng theo yêu cầu đã phân tích, bao gồm đăng ký/đăng nhập, phân quyền theo vai trò, quản lý thú cưng, đặt lịch, xử lý lịch hẹn tại phòng khám, tạo bệnh án, kê đơn thuốc, thanh toán VNPAY sandbox và báo cáo thống kê cho admin.

Ngoài kiểm thử chức năng, nhóm cũng kiểm tra các ràng buộc quan trọng về bảo mật và toàn vẹn dữ liệu: owner chỉ thao tác dữ liệu của mình, staff chỉ thao tác dữ liệu thuộc phòng khám được gán, admin có quyền quản trị, payment amount được tính ở backend và các dữ liệu nghiệp vụ quan trọng không bị xóa cứng.

## 3. Phạm vi đã kiểm thử

| Nhóm chức năng | Nội dung kiểm thử | Trạng thái |
|---|---|---|
| Unit testing backend | Kiểm thử service, serializer, controller và common helper | Đạt |
| Integration testing backend | Kiểm thử API, database test, authentication, permission và luồng nghiệp vụ chính | Đạt |
| Manual testing frontend | Kiểm thử thao tác trực tiếp trên giao diện theo vai trò owner, staff và admin | Đạt |

Lưu ý: phạm vi frontend trong báo cáo này chỉ bao gồm manual testing trên giao diện.

## 4. Kết quả unit test và integration test backend

### 4.1 Backend

Lệnh đã chạy:

```bash
cd backend
venv\Scripts\pytest.exe
```

Kết quả:

| Chỉ số | Kết quả |
|---|---:|
| Tổng số test case | 257 |
| Passed | 257 |
| Failed | 0 |
| Error | 0 |
| Warning | 1 |
| Thời gian chạy | 3.11 giây |

Ghi chú: warning phát sinh do pytest không tạo được cache trong `backend/.pytest_cache` vì lỗi quyền truy cập trên Windows. Warning này không ảnh hưởng đến kết quả pass/fail của test.

### 4.2 Coverage backend

Coverage report hiện có trong thư mục `backend/htmlcov` và ảnh tổng hợp tại `docs/CoverageReportPetCare.png`.

| Chỉ số | Kết quả |
|---|---:|
| Statements | 2383 |
| Covered | 2289 |
| Missing | 94 |
| Coverage | 96.06% |
| Ngưỡng yêu cầu trong `.coveragerc` | 80% |

Trong lần chạy lại với `pytest --cov=src`, quá trình coverage bị dừng do không có quyền xóa/ghi file `backend/.coverage`. Vì vậy báo cáo sử dụng kết quả coverage HTML đã được tạo sẵn trong repository.

## 5. Kết quả theo module backend

| Module test | Nhóm kiểm thử | Kết quả |
|---|---|---|
| `test_auth_api.py` | Integration API đăng ký, đăng nhập, profile, đổi mật khẩu | Passed |
| `test_pet_api.py` | Integration API hồ sơ thú cưng | Passed |
| `test_clinic_api.py` | Integration API phòng khám | Passed |
| `test_staff_admin_api.py` | Integration API admin/staff | Passed |
| `test_appointment_api.py` | Integration API đặt lịch và chuyển trạng thái lịch hẹn | Passed |
| `test_medical_record_api.py` | Integration API bệnh án | Passed |
| `test_prescription_api.py` | Integration API đơn thuốc và chi tiết đơn thuốc | Passed |
| `test_medicine_api.py` | Integration API thuốc | Passed |
| `test_payment_api.py` | Integration API thanh toán | Passed |
| `test_report_api.py` | Integration API báo cáo | Passed |
| `unit/services/*` | Business logic của các service chính | Passed |
| `unit/serializers/*` | Validate input và output serializer | Passed |
| `unit/controllers/*` | Controller/viewset mapping, permission và response | Passed |
| `unit/common/*` | Exception, response helper, permission, base model | Passed |

## 6. Kết quả manual testing frontend

| Mã | Kịch bản | Kết quả mong đợi | Trạng thái |
|---|---|---|---|
| MAN-01 | Owner đăng ký, đăng nhập và mở trang profile | Hiển thị đúng thông tin user, route được bảo vệ bằng token | Đạt |
| MAN-02 | Owner cập nhật hồ sơ cá nhân | Backend lưu thông tin mới, frontend cập nhật context/cookie và hiển thị thông báo thành công | Đạt |
| MAN-03 | Owner đổi mật khẩu | Kiểm tra mật khẩu hiện tại, lưu mật khẩu mới dạng hash, đăng nhập bằng mật khẩu mới thành công | Đạt |
| MAN-04 | Owner thêm/sửa/xóa mềm thú cưng | Dữ liệu pet được lưu đúng và chỉ owner sở hữu được thao tác | Đạt |
| MAN-05 | Owner đặt lịch khám/grooming | Appointment được tạo với trạng thái `PENDING`, không cho đặt lịch quá khứ hoặc slot trùng | Đạt |
| MAN-06 | Staff xác nhận, check-in, bắt đầu và hoàn tất lịch hẹn | Trạng thái chuyển đúng chuỗi nghiệp vụ đến `WAITING_PAYMENT`, hệ thống tạo payment `PENDING` | Đạt |
| MAN-07 | Staff tạo bệnh án và kê đơn thuốc | Bệnh án gắn đúng appointment/pet/clinic/staff, đơn thuốc trừ tồn kho đúng | Đạt |
| MAN-08 | Owner thanh toán lịch hẹn | Payment chuyển `PAID`, appointment chuyển `COMPLETED` sau khi thanh toán thành công | Đạt |
| MAN-09 | Admin quản lý clinic, staff, service | Admin xem/thêm/sửa/xóa mềm dữ liệu đúng quyền | Đạt |
| MAN-10 | Admin xem báo cáo | Báo cáo tổng hợp doanh thu, trạng thái lịch hẹn và hiệu suất phòng khám | Đạt |
| MAN-11 | User truy cập route sai vai trò | Frontend/API từ chối hoặc điều hướng về trang phù hợp | Đạt |

## 7. Defect và tồn đọng

| Mã lỗi | Mô tả | Mức độ | Trạng thái |
|---|---|---|---|
| ENV-01 | `pytest --cov=src` không chạy lại được do không có quyền ghi/xóa `backend/.coverage` | Low | Dùng coverage HTML có sẵn để báo cáo |
| ENV-02 | pytest không ghi được cache vào `.pytest_cache` | Low | Không ảnh hưởng kết quả test |

## 8. Đánh giá rủi ro

- Backend có độ ổn định tốt trong phạm vi test hiện tại: toàn bộ 257 test đều pass, coverage đạt trên ngưỡng yêu cầu.
- Các luồng nghiệp vụ trọng yếu như phân quyền, đặt lịch, bệnh án, đơn thuốc, thanh toán và báo cáo đã có cả unit test và integration test.
- Frontend được đánh giá bằng manual testing theo các luồng sử dụng chính.
- VNPAY sandbox cần tiếp tục kiểm thử tích hợp với cấu hình `.env` thật của môi trường demo, đặc biệt là return URL và IPN callback.

## 9. Kết luận

Backend của hệ thống đạt tiêu chí kiểm thử trong đợt này: 257/257 test unit và integration đều pass, coverage hiện có đạt 96.06%, cao hơn ngưỡng yêu cầu 80%.

Frontend được kiểm thử thủ công theo các luồng owner, staff và admin. Kết quả frontend trong báo cáo chỉ phản ánh manual testing trên giao diện.
