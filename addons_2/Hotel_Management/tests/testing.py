from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, AccessError
from datetime import datetime, timedelta
import logging

# Create a special logger to record security events
security_logger = logging.getLogger('hotel.security')
security_logger.setLevel(logging.INFO)

# Set up where to save the log file
file_handler = logging.FileHandler('security_tests.log')
file_handler.setLevel(logging.INFO)

# Make the log messages look nice with date and time
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Connect the logger to the file
security_logger.addHandler(file_handler)

class TestHotelManagementSecurity(TransactionCase):
    def setUp(self):
        # This runs before each test
        super(TestHotelManagementSecurity, self).setUp()
        
        # create three types of users:
        # 1. Normal employee
        # 2. Hotel manager
        # 3. Admin
        # If these groups don't exist, we create them
        self.env['res.groups'].search([('name', '=', 'Hotel Employee')]) or \
            self.env['res.groups'].create({'name': 'Hotel Employee'})
        self.env['res.groups'].search([('name', '=', 'Hotel Manager')]) or \
            self.env['res.groups'].create({'name': 'Hotel Manager'})
        self.env['res.groups'].search([('name', '=', 'Hotel Admin')]) or \
            self.env['res.groups'].create({'name': 'Hotel Admin'})

        # Create test users with different roles
        self.employee_user = self._create_user('employee_user', 'Hotel Employee')
        self.manager_user = self._create_user('manager_user', 'Hotel Manager')
        self.admin_user = self._create_user('admin_user', 'Hotel Admin')
        
        # Create test employees
        self.manager = self._create_employee('Test Manager', self.manager_user)
        self.employee = self._create_employee('Test Employee', self.employee_user, self.manager)

        # Create a test hotel
        self.hotel = self.env['hotel.management'].create({
            'name': 'Test Security Hotel',
            'address': 'Test Address',
            'floor_count': 5,
            'manager_id': self.manager.id,
            # replace all employees with just this one employee
            # [(6, 0, [ids])] clear all existing records and add these new ones
            'employee_ids': [(6, 0, [self.employee.id])]
        })

        # Create a test room in hotel
        self.room = self.env['hotel.room'].create({
            'name': '101',
            'hotel_id': self.hotel.id,
            'bed_type': 'single',
            'price': 100.0,
            'state': 'available'
        })

    def _create_user(self, login, group_name):
        # Helper function to create a new user
        # login: username for the new user
        # group_name: what type of user (employee, manager, or admin)
        user = self.env['res.users'].create({
            'name': f'Test {login}',
            'login': login,
            'password': 'test123',
            'groups_id': [(4, self.env.ref(f'Hotel_Management.group_{group_name.lower().replace(" ", "_")}').id)]
        })
        return user

    def _create_employee(self, name, user, manager=None):
        # Helper function to create a new employee
        # name: employee's name
        # user: link to their user account
        # manager: who is their boss (optional)
        vals = {
            'name': name,
            'user_id': user.id,
            'work_email': f'{name.lower().replace(" ", ".")}@test.com',
        }
        if manager:
            vals['parent_id'] = manager.id
        return self.env['hr.employee'].create(vals)

    def _log_security_event(self, event_type, user, target, result):
        # Helper function to write security events to our log file
        # Example: "User John tried to access Room 101 - Access Denied"
        security_logger.info(
            f"Security Event: {event_type} | User: {user} | Target: {target} | Result: {result}"
        )

    def test_unauthorized_booking_access(self):
        """Test what happens when someone tries to see a booking they shouldn't"""
        # Create a new booking
        booking = self.env['hotel.booking'].create({
            'name': 'Test Booking',
            'customer_name': 'Test Customer',
            'hotel_id': self.hotel.id,
            'room_type': 'single',
            'room_id': self.room.id,
            'check_in': datetime.now().date(),
            'check_out': (datetime.now() + timedelta(days=1)).date(),
        })

        # Try to access booking with wrong user
        # This should fail with AccessError
        with self.assertRaises(AccessError):
            other_employee = self._create_user('other_employee', 'Hotel Employee')
            booking.with_user(other_employee).read()
            self._log_security_event(
                'Unauthorized Booking Access',
                other_employee.name,
                f'Booking {booking.name}',
                'Access Denied'
            )

    def test_privilege_escalation(self):
        """Test what happens when an employee tries to do manager things"""
        # Create a new booking
        booking = self.env['hotel.booking'].create({
            'name': 'Test Booking',
            'customer_name': 'Test Customer',
            'hotel_id': self.hotel.id,
            'room_type': 'single',
            'room_id': self.room.id,
            'state': 'draft'
        })

        # Try to confirm booking as employee (should fail)
        with self.assertRaises(AccessError):
            booking.with_user(self.employee_user).write({'state': 'confirmed'})
            self._log_security_event(
                'Privilege Escalation Attempt',
                self.employee_user.name,
                f'Booking {booking.name}',
                'Access Denied'
            )

    def test_data_isolation(self):
        """Test if employees can only see their own hotel's data"""
        # Create another hotel with different employees
        other_manager = self._create_employee('Other Manager', self._create_user('other_manager', 'Hotel Manager'))
        other_hotel = self.env['hotel.management'].create({
            'name': 'Other Hotel',
            'address': 'Other Address',
            'floor_count': 3,
            'manager_id': other_manager.id,
        })

        # Try to read other hotel's data (should fail)
        with self.assertRaises(AccessError):
            other_hotel.with_user(self.employee_user).read()
            self._log_security_event(
                'Cross-Hotel Data Access Attempt',
                self.employee_user.name,
                f'Hotel {other_hotel.name}',
                'Access Denied'
            )

    def test_sql_injection_prevention(self):
        """Test if someone tries to hack with SQL injection"""
        # Try a basic SQL injection attack
        malicious_domain = [('name', '=', "' UNION SELECT id FROM res_users --")]
        results = self.env['hotel.booking'].search(malicious_domain)
        self.assertEqual(len(results), 0)
        self._log_security_event(
            'SQL Injection Attempt',
            self.env.user.name,
            'hotel.booking search',
            'Prevented'
        )

    def test_mass_assignment(self):
        """Test if employee can change important hotel data"""
        # Try to make an employee the manager (should fail)
        with self.assertRaises(AccessError):
            self.hotel.with_user(self.employee_user).write({
                'manager_id': self.employee.id,
            })
            self._log_security_event(
                'Mass Assignment Attempt',
                self.employee_user.name,
                f'Hotel {self.hotel.name}',
                'Access Denied'
            )

    def test_rate_limiting(self):
        """Test if someone is making too many requests too quickly"""
        # Count how many times we try
        attempts = 0
        max_attempts = 5
        start_time = datetime.now()

        # Try to make many requests quickly
        while attempts < max_attempts:
            self.env['hotel.booking'].with_user(self.employee_user).search([])
            attempts += 1

        # Record how long it took
        duration = (datetime.now() - start_time).total_seconds()
        self._log_security_event(
            'Rate Limit Test',
            self.employee_user.name,
            f'{attempts} requests in {duration:.2f} seconds',
            'Monitored'
        )