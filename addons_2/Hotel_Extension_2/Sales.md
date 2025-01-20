

# Các bảng trong module Sales (sale)

## 1. sale.order
Bảng quản lý đơn hàng bán:
- Lưu trữ thông tin đơn hàng/báo giá
- Theo dõi trạng thái: draft (nháp), sent (đã gửi), sale (đã bán), cancel (đã hủy)
- Quản lý thông tin khách hàng, địa chỉ giao/nhận hàng
- Tính toán tổng tiền, thuế, chiết khấu
- Theo dõi thanh toán và xác nhận đơn hàng

## 2. sale.order.line  
Bảng chi tiết đơn hàng:
- Lưu các dòng sản phẩm trong đơn hàng
- Thông tin về số lượng, đơn giá, thuế
- Tính toán thành tiền cho từng dòng
- Theo dõi số lượng đã giao/đã xuất hóa đơn
- Liên kết với sản phẩm và đơn vị tính

## 3. product.document
Bảng quản lý tài liệu sản phẩm:
- Lưu trữ tài liệu đính kèm cho sản phẩm
- Cấu hình hiển thị tài liệu:
  + hidden: Ẩn
  + quotation: Hiển thị trên báo giá 
  + sale_order: Hiển thị trên đơn hàng đã xác nhận

## 4. account.invoice.report
Bảng báo cáo hóa đơn:
- Mở rộng từ account.invoice.report
- Thêm thông tin về đội ngũ bán hàng (team_id)
- Phục vụ thống kê và báo cáo doanh số

## Các tính năng chính:

1. Quản lý quy trình bán hàng:
- Tạo báo giá
- Xác nhận đơn hàng
- Xuất hóa đơn
- Theo dõi thanh toán

2. Tích hợp:
- Quản lý khách hàng (CRM)
- Kế toán (Invoicing)
- Quản lý kho (Inventory)
- Phân quyền người dùng

3. Báo cáo:
- Doanh số bán hàng
- Hiệu suất nhân viên
- Phân tích khách hàng
- Theo dõi hóa đơn

4. Tính năng nâng cao:
- Chiến lược giá (Pricelists)
- Quản lý hợp đồng
- Tự động hóa quy trình
- Giao tiếp với khách hàng


# Chi tiết cấu trúc các bảng trong module Sales (sale)

## 1. sale.order (Đơn hàng bán)
### Các trường cơ bản:
- name: Char - Số đơn hàng
- date_order: Datetime - Ngày đặt hàng
- partner_id: Many2one - Khách hàng
- state: Selection - Trạng thái đơn hàng
  + draft: Nháp
  + sent: Đã gửi
  + sale: Đã bán
  + done: Hoàn thành
  + cancel: Đã hủy
- currency_id: Many2one - Loại tiền tệ
- amount_total: Float - Tổng tiền
- amount_tax: Float - Tiền thuế
- amount_untaxed: Float - Tiền trước thuế

### Các trường liên quan đến thanh toán:
- payment_term_id: Many2one - Điều khoản thanh toán
- invoice_status: Selection - Trạng thái hóa đơn
- invoice_ids: One2many - Các hóa đơn
- amount_paid: Float - Số tiền đã thanh toán
- amount_to_invoice: Float - Số tiền cần xuất hóa đơn

### Các trường khác:
- team_id: Many2one - Đội ngũ bán hàng
- user_id: Many2one - Nhân viên bán hàng
- company_id: Many2one - Công ty
- note: Text - Ghi chú

## 2. sale.order.line (Chi tiết đơn hàng)
### Các trường cơ bản:
- order_id: Many2one - Đơn hàng
- product_id: Many2one - Sản phẩm
- name: Text - Mô tả
- product_uom_qty: Float - Số lượng
- price_unit: Float - Đơn giá
- price_subtotal: Float - Thành tiền
- tax_id: Many2many - Thuế

### Các trường tính toán:
- discount: Float - Chiết khấu
- price_total: Float - Tổng tiền (có thuế)
- qty_delivered: Float - Số lượng đã giao
- qty_invoiced: Float - Số lượng đã xuất hóa đơn
- qty_to_invoice: Float - Số lượng cần xuất hóa đơn

## 3. product.document (Tài liệu sản phẩm)
- name: Char - Tên tài liệu
- attached_on_sale: Selection - Hiển thị trên:
  + hidden: Ẩn
  + quotation: Báo giá
  + sale_order: Đơn hàng đã xác nhận
- file: Binary - File đính kèm
- product_id: Many2one - Sản phẩm

## 4. account.move (Bút toán kế toán/Hóa đơn)
### Các trường liên quan đến bán hàng:
- team_id: Many2one - Đội ngũ bán hàng
- campaign_id: Many2one - Chiến dịch marketing
- medium_id: Many2one - Kênh marketing
- source_id: Many2one - Nguồn marketing
- sale_order_count: Integer - Số đơn hàng liên quan

## 5. account.move.line (Chi tiết bút toán)
- sale_line_ids: Many2many - Các dòng đơn hàng
- is_downpayment: Boolean - Là khoản thanh toán trước
- price_unit: Float - Đơn giá
- quantity: Float - Số lượng

## 6. crm.team (Đội ngũ bán hàng)
### Các trường thống kê:
- invoiced: Float - Doanh số đã xuất hóa đơn
- invoiced_target: Float - Mục tiêu doanh số
- quotations_count: Integer - Số báo giá
- quotations_amount: Float - Giá trị báo giá
- sales_to_invoice_count: Integer - Số đơn hàng cần xuất hóa đơn
- sale_order_count: Integer - Tổng số đơn hàng

## 7. product.product (Sản phẩm)
### Các trường liên quan đến bán hàng:
- sales_count: Float - Số lượng đã bán
- invoice_policy: Selection - Chính sách xuất hóa đơn
- expense_policy: Selection - Chính sách chi phí
- product_catalog_product_is_in_sale_order: Boolean - Có trong đơn hàng

## 8. account.analytic.line (Bút toán phân tích)
- so_line: Many2one - Dòng đơn hàng
- amount: Float - Số tiền
- unit_amount: Float - Số lượng
- product_id: Many2one - Sản phẩm

## 9. product.category (Danh mục sản phẩm)
- property_account_downpayment_categ_id: Many2one - Tài khoản thanh toán trước

## 10. payment.transaction (Giao dịch thanh toán)
### Các trường liên quan đến bán hàng:
- sale_order_ids: Many2many - Các đơn hàng
- sale_order_ids_nbr: Integer - Số đơn hàng

## 11. payment.provider (Nhà cung cấp thanh toán)
- so_reference_type: Selection - Loại tham chiếu đơn hàng
  + so_name: Theo số đơn hàng
  + partner: Theo mã khách hàng

## Các quan hệ chính:
1. sale.order -> sale.order.line (1:n)
2. sale.order -> account.move (1:n) qua invoice_ids
3. sale.order.line -> account.move.line (n:n)
4. sale.order -> crm.team (n:1)
5. sale.order -> payment.transaction (n:n)
6. product.product -> sale.order.line (1:n)