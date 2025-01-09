from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class TestHotelEdgeCases(TransactionCase):
    def setUp(self):
        super(TestHotelEdgeCases, self).setUp()
        # Create base test data
        self.manager = self.env['hr.employee'].create({
            'name': 'Edge Case Manager',
            'work_email': 'edge.manager@test.com',
        })
        
        self.hotel = self.env['hotel.management'].create({
            'name': 'Edge Case Hotel',
            'address': 'Test Address',
            'floor_count': 5,
            'manager_id': self.manager.id,
        })

    def test_zero_price_room(self):
        """Test creating room with zero price"""
        room = self.env['hotel.room'].create({
            'name': 'Z101',
            'hotel_id': self.hotel.id,
            'bed_type': 'single',
            'price': 0.0,
            'state': 'available'
        })
        self.assertEqual(room.price, 0.0, "Should allow zero price rooms")

    def test_long_stay_booking(self):
        """Test booking for extended period (>30 days)"""
        room = self.env['hotel.room'].create({
            'name': 'L101',
            'hotel_id': self.hotel.id,
            'bed_type': 'double',
            'price': 100.0,
        })
        
        # Create a 60-day booking
        check_in = datetime.now().date()
        check_out = check_in + timedelta(days=60)
        
        booking = self.env['hotel.booking'].create({
            'name': 'Long Stay Booking',
            'customer_name': 'Long Stay Guest',
            'hotel_id': self.hotel.id,
            'room_type': 'double',
            'room_id': room.id,
            'check_in': check_in,
            'check_out': check_out,
        })
        self.assertEqual(booking.state, 'draft', "Long stay booking should be created in draft state")

    def test_same_day_checkout(self):
        """Test booking with same day check-in/check-out"""
        room = self.env['hotel.room'].create({
            'name': 'S101',
            'hotel_id': self.hotel.id,
            'bed_type': 'single',
            'price': 50.0,
        })
        
        today = datetime.now().date()
        with self.assertRaises(ValidationError):
            self.env['hotel.booking'].create({
                'name': 'Same Day Stay',
                'customer_name': 'Day Guest',
                'hotel_id': self.hotel.id,
                'room_type': 'single',
                'room_id': room.id,
                'check_in': today,
                'check_out': today,
            })

    def test_multiple_room_features(self):
        """Test room with multiple features"""
        features = self.env['hotel.room.feature'].create([
            {
                'name': f'Feature {i}',
                'description': f'Test Feature {i}',
                'feature_type': type
            }
            for i, type in enumerate(['comfort', 'luxury', 'basic'], 1)
        ])
        
        room = self.env['hotel.room'].create({
            'name': 'M101',
            'hotel_id': self.hotel.id,
            'bed_type': 'double',
            'price': 150.0,
            'feature_ids': [(6, 0, features.ids)]
        })
        
        self.assertEqual(len(room.feature_ids), 3, "Room should have all 3 features")

    def test_concurrent_bookings(self):
        """Test multiple bookings for same room with gap"""
        room = self.env['hotel.room'].create({
            'name': 'C101',
            'hotel_id': self.hotel.id,
            'bed_type': 'single',
            'price': 75.0,
        })
        
        # Create first booking
        booking1 = self.env['hotel.booking'].create({
            'name': 'First Booking',
            'customer_name': 'First Guest',
            'hotel_id': self.hotel.id,
            'room_type': 'single',
            'room_id': room.id,
            'check_in': datetime.now().date(),
            'check_out': (datetime.now() + timedelta(days=3)).date(),
        })
        booking1.action_confirm()
        
        # Create second booking with 1-day gap
        booking2 = self.env['hotel.booking'].create({
            'name': 'Second Booking',
            'customer_name': 'Second Guest',
            'hotel_id': self.hotel.id,
            'room_type': 'single',
            'room_id': room.id,
            'check_in': (datetime.now() + timedelta(days=4)).date(),
            'check_out': (datetime.now() + timedelta(days=7)).date(),
        })
        booking2.action_confirm()
        
        self.assertEqual(booking2.state, 'confirmed', "Second booking should be confirmed")

    def test_hotel_full_capacity(self):
        """Test hotel at full capacity"""
        # Create multiple rooms
        rooms = self.env['hotel.room'].create([
            {
                'name': f'R10{i}',
                'hotel_id': self.hotel.id,
                'bed_type': 'single',
                'price': 100.0,
                'state': 'available'
            }
            for i in range(5)
        ])
        
        # Book all rooms for same period
        check_in = datetime.now().date()
        check_out = check_in + timedelta(days=1)
        
        for i, room in enumerate(rooms):
            booking = self.env['hotel.booking'].create({
                'name': f'Booking {i+1}',
                'customer_name': f'Guest {i+1}',
                'hotel_id': self.hotel.id,
                'room_type': 'single',
                'room_id': room.id,
                'check_in': check_in,
                'check_out': check_out,
            })
            booking.action_confirm()
        
        # Verify all rooms are booked
        available_rooms = rooms.filtered(lambda r: r.state == 'available')
        self.assertEqual(len(available_rooms), 0, "All rooms should be booked")

    def test_booking_state_changes(self):
        """Test booking state transitions"""
        room = self.env['hotel.room'].create({
            'name': 'B101',
            'hotel_id': self.hotel.id,
            'bed_type': 'single',
            'price': 100.0,
        })
        
        booking = self.env['hotel.booking'].create({
            'name': 'State Test Booking',
            'customer_name': 'Test Guest',
            'hotel_id': self.hotel.id,
            'room_type': 'single',
            'room_id': room.id,
            'check_in': datetime.now().date(),
            'check_out': (datetime.now() + timedelta(days=1)).date(),
        })
        
        # Test state changes
        self.assertEqual(booking.state, 'draft', "Initial state should be draft")
        booking.action_confirm()
        self.assertEqual(booking.state, 'confirmed', "State should be confirmed after confirmation")
        self.assertEqual(booking.room_id.state, 'booked', "Room state should be booked")
