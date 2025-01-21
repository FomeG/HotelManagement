from odoo import models, fields, api, tools
from datetime import datetime, timedelta

class HotelRevenueReport(models.Model):
    _name = 'hotel.revenue.report'
    _description = 'Hotel Revenue Report'
    _auto = False

    date = fields.Date('Date')
    hotel_id = fields.Many2one('hotel.management', 'Hotel')
    room_id = fields.Many2one('hotel.room', 'Room')
    booking_id = fields.Many2one('hotel.booking', 'Booking')
    room_revenue = fields.Float('Room Revenue')
    service_revenue = fields.Float('Service Revenue')
    total_revenue = fields.Float('Total Revenue', compute='_compute_total_revenue', store=True)
    customer_id = fields.Many2one('res.partner', 'Customer')
    room_type = fields.Selection(related='room_id.bed_type', string='Room Type')
    
    @api.depends('room_revenue', 'service_revenue')
    def _compute_total_revenue(self):
        for record in self:
            record.total_revenue = record.room_revenue + record.service_revenue

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                WITH booking_revenues AS (
                    SELECT 
                        b.id as booking_id,
                        b.hotel_id,
                        b.room_id,
                        b.check_in as date,
                        b.total_room_price as room_revenue,
                        b.customer_name as customer_id,
                        COALESCE(SUM(sl.price_total), 0) as service_revenue
                    FROM hotel_booking b
                    LEFT JOIN hotel_booking_service_line sl ON sl.booking_id = b.id
                    WHERE b.state in ('checkin', 'checkout')
                    GROUP BY b.id, b.hotel_id, b.room_id, b.check_in, b.total_room_price, b.customer_name
                )
                SELECT
                    row_number() OVER () AS id,
                    br.date,
                    br.hotel_id,
                    br.room_id,
                    br.booking_id,
                    br.customer_id,
                    br.room_revenue,
                    br.service_revenue
                FROM booking_revenues br
            )
        """ % self._table)