# Challenge: Xây Dựng Module Quản Lý Khách Sạn

## Mô tả bài tập

Thiết kế và phát triển một module Odoo hoàn chỉnh để quản lý hoạt động của khách sạn, bao gồm quản lý phòng, đặt phòng (booking), theo dõi trạng thái sử dụng phòng, và tích hợp các module khác như Sales, Inventory, và POS. Module này sẽ hỗ trợ nhân viên và khách hàng trong việc kiểm tra phòng trống, đặt phòng, thanh toán hóa đơn, và phân tích doanh thu.

## Yêu cầu cụ thể

### 1. Quản lý phòng khách sạn
- Tạo model room để quản lý thông tin phòng:
  - Số phòng, loại phòng (single, double, suite), giá theo ngày (cuối tuần sẽ đắt hơn trong tuần)
  - Trạng thái phòng: trống, đang sử dụng, bảo trì

- Tạo giao diện để thêm, chỉnh sửa thông tin phòng

### 2. Quản lý đặt phòng (Booking)
- Tạo model booking:
  - Gồm khách hàng, phòng, ngày check-in, ngày check-out, số ngày lưu trú
  - Tự động tính tổng tiền phòng

- Tích hợp với module sales để tạo hóa đơn (SO) từ đơn đặt phòng
- Xử lý logic kiểm tra phòng trống trước khi đặt

### 3. Quản lý thực tế sử dụng phòng
- Cập nhật trạng thái phòng khi khách check-in, check-out
- Ghi nhận khách hàng sử dụng vật phẩm trong phòng (e.g, snack, beer, wines)
- Ghi nhận khách hàng sử dụng thêm dịch vụ (e.g., minibar, spa)

### 4. Tích hợp module Inventory
- Quản lý các sản phẩm/dịch vụ khách sử dụng (e.g., nước uống, đồ ăn) từ inventory
- Tạo hóa đơn bán hàng (SO) bao gồm cả tiền phòng và sản phẩm thêm

### 5. Màn hình booking cho khách hàng
- Xây dựng giao diện (portal hoặc OWL) cho khách:
  - Hiển thị danh sách phòng trống
  - Đặt phòng trực tuyến, chọn ngày check-in và check-out

- Xây dựng giao diện để khách lưu trú có thể:
  - Order hoặc mua thêm các self-service như wifi, laundry
  - Order các dịch vụ miễn phí như dọn phòng, collect quần áo bẩn

### 6. Báo cáo
- Báo cáo phòng trống:
  - Danh sách các phòng trống trong ngày hoặc theo khoảng thời gian
- Báo cáo doanh thu:
  - Tổng doanh thu theo ngày, tuần, tháng
  - Doanh thu chi tiết từng phòng hoặc từng khách hàng

### 7. Tích hợp POS (Point of Sale)
- Cho phép thêm các sản phẩm (e.g., đồ ăn, thức uống) qua POS
- Kết hợp các sản phẩm POS vào hóa đơn khách sạn

## Hướng dẫn triển khai

### 1. Module Structure
- Models:
  - `room.py`: Quản lý thông tin phòng
  - `booking.py`: Quản lý đặt phòng
  - `report.py`: Quản lý báo cáo

- Views:
  - Form view, list view cho phòng và đặt phòng
  - Giao diện booking trên portal

- Data:
  - Demo data cho phòng và dịch vụ khách sạn

- Integration:
  - Kết nối với sale.order, inventory.product, và pos.order

### 2. Chức năng chi tiết
- Room Management:
  - @api.depends để tính trạng thái phòng dựa trên đặt phòng hiện tại
- Booking Logic:
  - Constraint kiểm tra phòng trống trước khi lưu đặt phòng

- Invoice Integration:
  - Tự động tạo dòng hóa đơn từ tiền phòng và dịch vụ

- POS Integration:
  - API ghi nhận dịch vụ khách dùng từ POS và đồng bộ vào booking

### 3. Báo cáo
- Báo cáo dùng QWeb hoặc Pivot View:
  - Báo cáo doanh thu chi tiết và tổng hợp
  - Báo cáo trạng thái phòng

## Deliverables
- Source Code: Module Odoo hoàn chỉnh
- Demo Data: Thêm sẵn dữ liệu phòng, khách hàng, và dịch vụ
- Documentation: Hướng dẫn cài đặt, sử dụng và mở rộng module
- Report Outputs: Xuất báo cáo phòng trống và doanh thu


# NOTE:
- ODOO 18 DOES NOT HAVE TREE, USE <LIST> INSTEAD
- ODOO 18 DOES NOT HAVE ATTRS, USE VISIBLE OR INVISIBLE INSTEAD