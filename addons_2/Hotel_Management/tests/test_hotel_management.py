from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class TestHotelManagement(TransactionCase):

    def setUp(self):
        super(TestHotelManagement, self).setUp()
        # Tạo dữ liệu test
        
        # Tạo employee làm manager
        self.manager = self.env['hr.employee'].create({
            'name': 'Test Manager',
            'work_email': 'manager@test.com',
        })
        
        # Tạo employee làm nhân viên
        self.employee = self.env['hr.employee'].create({
            'name': 'Test Employee',
            'work_email': 'employee@test.com',
            'parent_id': self.manager.id,
        })

        # Tạo hotel
        self.hotel = self.env['hotel.management'].create({
            'name': 'Test Hotel',
            'address': 'Test Address',
            'floor_count': 5,
            'manager_id': self.manager.id,
            'employee_ids': [(6, 0, [self.employee.id])]
        })

        # Tạo room feature
        self.feature = self.env['hotel.room.feature'].create({
            'name': 'Test Feature',
            'description': 'Test Description',
            'feature_type': 'comfort'
        })

        # Tạo room
        self.room = self.env['hotel.room'].create({
            'name': '101',
            'hotel_id': self.hotel.id,
            'bed_type': 'single',
            'price': 100.0,
            'state': 'available',
            'feature_ids': [(6, 0, [self.feature.id])]
        })

    def test_create_booking(self):
        """Test tạo booking mới"""
        booking = self.env['hotel.booking'].create({
            'name': 'Test Booking',
            'customer_name': 'Test Customer',
            'hotel_id': self.hotel.id,
            'room_type': 'single',
            'room_id': self.room.id,
            'check_in': datetime.now().date(),
            'check_out': (datetime.now() + timedelta(days=1)).date(),
        })
        self.assertEqual(booking.state, 'draft')

    def test_confirm_booking(self):
        """Test xác nhận booking"""
        booking = self.env['hotel.booking'].create({
            'name': 'Test Booking',
            'customer_name': 'Test Customer',
            'hotel_id': self.hotel.id,
            'room_type': 'single',
            'room_id': self.room.id,
            'check_in': datetime.now().date(),
            'check_out': (datetime.now() + timedelta(days=1)).date(),
        })
        booking.action_confirm()
        self.assertEqual(booking.state, 'confirmed')
        self.assertEqual(booking.room_id.state, 'booked')

    def test_invalid_dates(self):
        """Test validation ngày check-in/check-out"""
        with self.assertRaises(ValidationError):
            self.env['hotel.booking'].create({
                'name': 'Test Booking',
                'customer_name': 'Test Customer',
                'hotel_id': self.hotel.id,
                'room_type': 'single',
                'room_id': self.room.id,
                'check_in': (datetime.now() + timedelta(days=1)).date(),
                'check_out': datetime.now().date(),  # check_out trước check_in
            })

    def test_room_double_booking(self):
        """Test không cho phép book trùng phòng"""
        # Tạo booking đầu tiên
        booking1 = self.env['hotel.booking'].create({
            'name': 'Test Booking 1',
            'customer_name': 'Test Customer 1',
            'hotel_id': self.hotel.id,
            'room_type': 'single',
            'room_id': self.room.id,
            'check_in': datetime.now().date(),
            'check_out': (datetime.now() + timedelta(days=2)).date(),
        })
        booking1.action_confirm()

        # Thử tạo booking thứ 2 trùng thời gian
        with self.assertRaises(ValidationError):
            booking2 = self.env['hotel.booking'].create({
                'name': 'Test Booking 2',
                'customer_name': 'Test Customer 2',
                'hotel_id': self.hotel.id,
                'room_type': 'single',
                'room_id': self.room.id,
                'check_in': datetime.now().date(),
                'check_out': (datetime.now() + timedelta(days=1)).date(),
            })
            booking2.action_confirm()

    def test_compute_room_count(self):
        """Test tính toán số lượng phòng"""
        # Tạo thêm 1 phòng mới
        self.env['hotel.room'].create({
            'name': '102',
            'hotel_id': self.hotel.id,
            'bed_type': 'double',
            'price': 200.0,
            'state': 'available'
        })
        self.assertEqual(self.hotel.room_count, 2)