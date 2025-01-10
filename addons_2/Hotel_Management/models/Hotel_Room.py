from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.http import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)  # define the logger


class HotelRoom(models.Model):
    # Basic setup info
    _name = 'hotel.room'  # Technical name
    _description = 'Hotel Room'  # Display title

    # Define important fields
    hotel_id = fields.Many2one('hotel.management', 'Hotel', required=True)  # Link to hotel (req)
    
    
    hotel_address = fields.Text(related='hotel_id.address', string='Hotel Address')  # Hotel addr (from hotel_id)
    
    name = fields.Char('Room Number', required=True)  # Room num (req)
    
    bed_type = fields.Selection([
        ('single', 'Single'),  # Single bed
        ('double', 'Double')   # Double bed
    ], string='Bed Type', required=True)  # Bed type (req)
    price = fields.Float('Price')  # Room price
    state = fields.Selection([
        ('available', 'Available'),  # Status: empty
        ('booked', 'Booked')        # Status: booked
    ], string='Status', default='available')  # Room status, default = available
    feature_ids = fields.Many2many('hotel.room.feature', string='Features')  # Room features list (m2m)
    # last_booking_date = fields.Datetime('Last Booking Date')
    last_booking_date = fields.Date(string='Last Booking Date', compute='_compute_last_booking_date')


    # SQL Constraint: Room number must be unique within same hotel
    _sql_constraints = [
        ('room_hotel_uniq', 'unique(name, hotel_id)', 'Room number must be unique within the same hotel!')
    ]
    
    
    
    #region Cronjob# get email information form the xml defined in the email_config.xml file in data folder TO AVOID HHARDCODE
    def get_email_config(self):
        IrConfigParam = self.env['ir.config_parameter'].sudo()
        return {
            'email_from': IrConfigParam.get_param('hotel.alert_email_from'), # get value from this key (my email :)
            'email_to': IrConfigParam.get_param('hotel.alert_email_to'),
        }
    
    # cronjob_sending_emails
    def cron_check_unrented_rooms(self):
        rooms = self.search([('state', '=', 'available')])
        unrented_rooms = []
        
                                                    # 7 days
        unrented_time = (datetime.now() - timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
        
        for room in rooms:
            bookings = self.env['hotel.booking'].search_count([
                ('room_id', '=', room.id),
                ('state', '=', 'confirmed'),
                ('create_date', '>=', unrented_time)
            ])
            
            # collect rooms with no bookings in the past 7 days
            if bookings == 0:
                unrented_rooms.append({
                    'name': room.name,
                    'price': room.price,
                    'state': dict(room._fields['state'].selection).get(room.state)
                })
        
        # only send email if there are unrented rooms
        if unrented_rooms:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Get email configuration
            email_config = self.get_email_config()
            
            if not email_config['email_from'] or not email_config['email_to']:
                _logger.error('Email configuration is missing for unrented rooms alert')
                return
            
            # build HTML table for rooms
            rooms_html = '''
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding: 8px;">Room Number</th>
                        <th style="padding: 8px;">Price (VND)</th>
                        <th style="padding: 8px;">Status</th>
                    </tr>
            '''
            
            for room in unrented_rooms:
                rooms_html += f'''
                    <tr>
                        <td style="padding: 8px;">{room['name']}</td>
                        <td style="padding: 8px;">{room['price']}</td>
                        <td style="padding: 8px;">{room['state']}</td>
                    </tr>
                '''
            
            rooms_html += '</table>'
            
            mail_values = {
                'subject': f'Alert: {len(unrented_rooms)} rooms haven\'t been booked in the past 7 days!',
                'email_from': email_config['email_from'],
                'email_to': email_config['email_to'],
                'body_html': f'''
                    <div>
                        <p>The following rooms have had no bookings in the past 7 days:</p>
                        {rooms_html}
                        <p>Time: {current_time}</p>
                    </div>
                '''
            }
            
            # sendmail with the superuser (because this is a cronjob, meaning its automated -> need admin privileges)
            self.env['mail.mail'].sudo().create(mail_values).send()
            
            
    #endregion
        
        
    @api.depends('hotel_id', 'name')
    def _compute_last_booking_date(self):
        for record in self:
            if record.hotel_id and record.name:
                # Tìm booking gần nhất của phòng này trong bảng hotel.booking
                last_booking = self.env['hotel.booking'].search([
                    ('room_id', '=', record.id),
                    ('state', '=', 'confirmed')  # Chỉ lấy các booking đã confirmed
                ], order='check_in desc', limit=1)  # Sắp xếp theo check_in date thay vì booking_date
                
                record.last_booking_date = last_booking.check_in if last_booking else False
            else:
                record.last_booking_date = False
                
                

    # Add this method for the automated action
    def check_unbooked_rooms(self):
        # Get rooms that haven't been booked in 7 days
        seven_days_ago = datetime.now() - timedelta(minutes=1)
        unbooked_rooms = self.search([
            '|',
            ('last_booking_date', '<', seven_days_ago),
            ('last_booking_date', '=', False)
        ])
        
        for room in unbooked_rooms:
            _logger.info(f"Room {room.name} in hotel {room.hotel_id.name} hasn't been booked for over a week")
    
        