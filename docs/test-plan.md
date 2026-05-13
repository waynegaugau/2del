# Test Plan

## 1. Mục tiêu
Đảm bảo hệ thống phòng khám thú y 2DEL hoạt động đúng các luồng chính: đăng nhập, phân quyền, quản lý thú cưng, đặt lịch, khám bệnh, kê đơn, thanh toán VNPAY sandbox và báo cáo thống kê.

## 2. Phạm vi kiểm thử
- Backend API: authentication, users, clinics, staff, pets, appointments, medical records, prescriptions, medicines, payments, reports.
- Frontend: các màn hình owner, staff, admin; điều hướng; gọi API; hiển thị thông báo lỗi/thành công.
- Tích hợp: JWT authentication, phân quyền theo vai trò, VNPAY sandbox, kết nối MySQL.

## 3. Loại kiểm thử
- Unit test: kiểm tra service, serializer, controller và helper riêng lẻ.
- Integration test: kiểm tra API endpoint, database, authentication và permission.
- UI/manual test: kiểm tra thao tác trên giao diện React theo từng vai trò.
- Build/lint test: đảm bảo frontend build được và không có lỗi lint nghiêm trọng.
- Regression test: chạy lại các test quan trọng sau khi sửa logic đặt lịch, thanh toán hoặc phân quyền.

## 4. Môi trường kiểm thử
- Backend: Python 3.13+, Django 6, Django REST Framework, pytest, pytest-django.
- Frontend: Node.js 18+, React 19, Vite.
- Database: MySQL, có thể dùng database test riêng.
- Payment: VNPAY sandbox.

## 5. Các kịch bản chính
| Module | Nội dung cần kiểm tra | Kết quả mong đợi |
|--------|------------------------|------------------|
| Authentication | Đăng ký, đăng nhập, refresh token, logout | Trả về token hợp lệ, chặn tài khoản/thông tin sai |
| Phân quyền | Owner, staff, admin truy cập đúng màn hình/API | Role không phù hợp bị từ chối |
| Thú cưng | Thêm, sửa, xóa, xem danh sách thú cưng | Dữ liệu được lưu và chỉ owner liên quan được xem |
| Đặt lịch | Tạo lịch, xem lịch, cập nhật trạng thái | Trạng thái lịch thay đổi đúng quy trình |
| Khám bệnh | Check-in, bắt đầu khám, tạo hồ sơ y tế | Hồ sơ khám gắn đúng lịch hẹn và thú cưng |
| Đơn thuốc | Thêm thuốc, kê đơn, xem chi tiết đơn | Đơn thuốc hiển thị đúng thông tin và số lượng |
| Thanh toán | Tạo payment, redirect VNPAY, nhận kết quả thanh toán | Payment `PAID`, lịch hẹn `COMPLETED` khi thành công |
| Admin | Quản lý clinic, staff, service | Admin thêm/sửa/xóa/xem dữ liệu đúng |
| Báo cáo | Thống kê doanh thu, trạng thái lịch hẹn | Số liệu tổng hợp đúng theo bộ lọc |
| Frontend | Form validation, loading, toast, protected route | Giao diện phản hồi rõ ràng, không crash |

## 6. Lệnh chạy kiểm thử
Chạy test backend:

```bash
cd backend
venv\Scripts\activate
pytest
```

Chạy coverage backend:

```bash
cd backend
venv\Scripts\activate
pytest --cov=src
```

Kiểm tra frontend:

```bash
cd frontend
npm run lint
npm run build
```

## 7. Tiêu chí đạt
- Tất cả test backend pass.
- Frontend lint và build thành công.
- Các luồng manual quan trọng theo 3 vai trò không phát sinh lỗi nghiêm trọng.
- Các lỗi liên quan đến bảo mật, phân quyền, thanh toán và mất dữ liệu phải được sửa trước khi bàn giao.

## 8. Rủi ro cần lưu ý
- Sai phân quyền có thể làm lộ dữ liệu của owner hoặc chức năng admin.
- Lỗi xử lý trạng thái lịch hẹn có thể làm sai quy trình khám/thanh toán.
- VNPAY sandbox phụ thuộc cấu hình `.env`, cần kiểm tra kỹ callback/IPN.
- Báo cáo doanh thu cần đối chiếu với dữ liệu payment để tránh thống kê sai.
