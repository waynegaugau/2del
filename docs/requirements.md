
# Hệ thống quản lý thú cưng/phòng khám thú y - Requirements

----------

## 1. Actors

Hệ thống có 3 tác nhân chính:

-   **Chủ thú cưng (Pet Owner)**
    
-   **Phòng khám/Groomer (Business User)**
    
-   **Admin (System Admin)**
    

----------

## 2. Functional Requirements

### 2.1 Chủ thú cưng

-   Tạo và quản lý hồ sơ thú cưng
    
-   Đặt lịch khám/grooming
    
-   Thanh toán dịch vụ
    

### 2.2 Phòng khám/Groomer

-   Quản lý lịch hẹn và check-in
    
-   Quản lý hồ sơ bệnh án
    
-   Kê đơn và quản lý thuốc
    

### 2.3 Admin

-   Quản lý phòng khám (CRUD)
    
-   Quản lý tài khoản bác sĩ/nhân viên
    
-   Quản lý danh mục dịch vụ
    

----------

## 3. Global Business Rules

-   Không xóa cứng dữ liệu đã phát sinh (appointment, medical record, payment)
    
-   Mọi dữ liệu phải có audit log (created_at, updated_at)
    
-   Phân quyền theo role và clinic
    
-   Dữ liệu thú cưng là trung tâm của hệ thống
    

----------

## 4. Use Case Diagram

  

<p  align="center">

<img  src="UseCasePetCare.png"  width="700">

</p>

  

----------

## 5. Use Case Specifications

----------

# UC01 - Đặt lịch khám/Grooming

|Thuộc tính | Mô tả |
|---|---|
| Use case ID | UC01 |
| Actor chính | Chủ thú cưng |
|Actor phụ | Phòng khám/Groomer |
| Mô tả | Chủ thú cưng đặt lịch khám hoặc grooming |

### Pre-conditions

-   Người dùng đã đăng nhập
    
-   Có ít nhất 1 hồ sơ thú cưng
    
-   Phòng khám đang hoạt động
    

### Post-conditions

-   Tạo lịch hẹn mới
    
-   Trạng thái: Pending hoặc Confirmed
    

### Input

-   petId
    
-   serviceId
    
-   clinicId
    
-   datetime
    
-   note
    

### Output

-   appointmentId
    
-   status
    

### Business Rules

-   Không cho đặt lịch trong quá khứ
    
-   Không cho đặt trùng lịch của cùng thú cưng
    
-   Phải nằm trong giờ làm việc của phòng khám
    
-   Slot phải còn trống
    
-   Có thể cần phòng khám xác nhận (Pending)
    

### Main Flow

1.  User chọn thú cưng
    
2.  Chọn dịch vụ
    
3.  Chọn phòng khám
    
4.  Chọn thời gian
    
5.  Hệ thống kiểm tra slot khả dụng
    
6.  User xác nhận
    
7.  Hệ thống tạo lịch
    
8.  Gửi thông báo
    

### Alternative Flow

A1 - Không có slot trống  
→ Gợi ý thời gian khác

### Exception Flow

E1 - Lỗi hệ thống  
→ Hiển thị lỗi

----------

# UC02 - Quản lý lịch hẹn & Check-in

| Thuộc tính | Mô tả |
|---|---|
| Use case ID | UC02 |
| Actor chính | Phòng khám/Groomer |
| Actor phụ | Chủ thú cưng |

### Pre-conditions

-   Lịch hẹn tồn tại
    
-   Nhân viên có quyền truy cập
    

### Post-conditions

-   Trạng thái được cập nhật (Checked-in, Completed)
    

### Business Rules

-   Không check-in lịch đã hủy
    
-   Chỉ check-in lịch đã Confirmed
    
-   Có thể đánh dấu No-show
    

### Main Flow

1.  Nhân viên xem lịch
    
2.  Chọn lịch hẹn
    
3.  Khi khách đến → Check-in
    
4.  Hệ thống cập nhật trạng thái
    

### Alternative Flow

A1 - Khách đến trễ  
→ Reschedule hoặc No-show

### Exception Flow

E1 - Lỗi cập nhật  
→ Thông báo lỗi

----------

# UC03 - Quản lý phòng khám (CRUD)

| Thuộc tính | Mô tả |
|---|---|
| Use case ID | UC03 |
| Actor chính | Admin |

### Pre-conditions

-   Admin đăng nhập
    

### Post-conditions

-   Phòng khám được tạo/sửa/disable
    

### Business Rules

-   Không xóa phòng khám đã có dữ liệu
    
-   Dùng disable thay vì delete
    
-   Clinic phải unique
    

### Main Flow

1.  Admin mở màn hình quản lý
    
2.  Chọn thêm/sửa/xóa
    
3.  Nhập dữ liệu
    
4.  Validate
    
5.  Lưu
    

### Alternative Flow

A1 - Dữ liệu không hợp lệ  
→ Yêu cầu nhập lại

### Exception Flow

E1 - Lỗi hệ thống  
→ Hiển thị lỗi

----------

## 6. ĐẶC TẢ LUỒNG NGHIỆP VỤ – PET CARE (Business Flow Specifications)

----------

## 1. Luồng Đặt Lịch Khám/Grooming (Appointment Booking Flow)

**Mục tiêu:** Cho phép chủ thú cưng đặt lịch khám/grooming tại phòng khám phù hợp với thời gian mong muốn.

### Bước 1 (Frontend)

Người dùng nhập/chọn:

-   Thú cưng
    
-   Loại dịch vụ (khám, tiêm, grooming…)
    
-   Phòng khám
    
-   Ngày và khung giờ
    
-   Ghi chú (triệu chứng nếu có)
    

----------

### Bước 2 (API)

Frontend gọi API:

```http
POST /api/appointments

```

Payload:

```json
{
  "petId": "...",
  "serviceId": "...",
  "clinicId": "...",
  "datetime": "...",
  "note": "..."
}

```

----------

### Bước 3 (Backend)

-   Kiểm tra petId thuộc user hiện tại
    
-   Kiểm tra phòng khám đang hoạt động
    
-   Kiểm tra dịch vụ hợp lệ tại phòng khám
    
-   Kiểm tra khung giờ:
    
    -   Không nằm ngoài giờ làm việc
        
    -   Không bị trùng với booking khác
        
    -   Slot còn trống
        
-   Xác định trạng thái:
    
    -   `PENDING` (nếu cần xác nhận)
        
    -   hoặc `CONFIRMED` (auto confirm)
        

----------

### Bước 4 (Kết quả)

-   Tạo bản ghi Appointment
    
-   Trả về thông tin lịch hẹn
    
-   Gửi thông báo cho:
    
    -   Chủ thú cưng
        
    -   Phòng khám
        

----------

## 2. Luồng Check-in tại Phòng Khám (Check-in Flow)

**Mục tiêu:** Xác nhận thú cưng đã đến phòng khám và bắt đầu quá trình khám/chăm sóc.

### Bước 1 (Frontend)

Nhân viên:

-   Mở danh sách lịch hẹn trong ngày
    
-   Chọn lịch hẹn tương ứng
    

----------

### Bước 2 (API)

```http
POST /api/appointments/{id}/check-in

```

----------

### Bước 3 (Backend)

-   Kiểm tra appointment tồn tại
    
-   Kiểm tra trạng thái phải là `CONFIRMED`
    
-   Kiểm tra chưa bị hủy
    
-   Ghi nhận thời gian check-in
    
-   Cập nhật trạng thái → `CHECKED_IN`
    

----------

### Bước 4 (Kết quả)

-   Trả về appointment đã cập nhật
    
-   Cho phép chuyển sang trạng thái `IN_PROGRESS`
    

----------

## 3. Luồng Tạo Bệnh Án (Medical Record Flow)

**Mục tiêu:** Lưu thông tin khám, chẩn đoán và điều trị cho thú cưng.

### Bước 1 (Frontend)

Bác sĩ:

-   Mở hồ sơ từ lịch đã check-in
    
-   Nhập:
    
    -   Triệu chứng
        
    -   Chẩn đoán
        
    -   Hướng điều trị
        
    -   Ghi chú
        

----------

### Bước 2 (API)

```http
POST /api/medical-records

```

Payload:

```json
{
  "petId": "...",
  "appointmentId": "...",
  "symptoms": "...",
  "diagnosis": "...",
  "treatment": "...",
  "note": "..."
}

```

----------

### Bước 3 (Backend)

-   Kiểm tra quyền bác sĩ
    
-   Kiểm tra appointment hợp lệ
    
-   Gắn record với pet + appointment
    
-   Lưu lịch sử khám
    
-   Set trạng thái:
    
    -   `OPEN`
        
    -   hoặc `FOLLOW_UP_REQUIRED`
        

----------

### Bước 4 (Kết quả)

-   Trả về medical record
    
-   Cho phép tiếp tục kê đơn thuốc
    

----------

## 4. Luồng Thanh Toán (Payment Flow)

**Mục tiêu:** Xử lý thanh toán dịch vụ khám/grooming hoặc đơn thuốc.

### Bước 1 (Frontend)

Người dùng:

-   Chọn lịch hẹn hoặc hóa đơn
    
-   Chọn phương thức thanh toán
    

----------

### Bước 2 (API)

```http
POST /api/payments

```

Payload:

```json
{
  "appointmentId": "...",
  "amount": 500000,
  "method": "ONLINE"
}

```

----------

### Bước 3 (Backend)

-   Kiểm tra giao dịch hợp lệ
    
-   Kiểm tra chưa thanh toán
    
-   Gửi request tới payment gateway
    
-   Nhận callback:
    
    -   Success → `PAID`
        
    -   Fail → `FAILED`
        

----------

### Bước 4 (Kết quả)

-   Cập nhật trạng thái payment
    
-   Tạo hóa đơn
    
-   Gửi thông báo cho user
    

----------