from odoo import models, fields, api, tools

class HotelRoomReport(models.Model):
    _name = 'hotel.room.report'
    _description = 'Hotel Room Report'
    _auto = False

    date = fields.Date('Date')
    room_id = fields.Many2one('hotel.room', 'Room')
    state = fields.Selection([
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('maintenance', 'Maintenance'),
        ('reserved', 'Reserved')
    ], string='Status')
    hotel_id = fields.Many2one('hotel.management', 'Hotel')
    bed_type = fields.Selection([
        ('single', 'Single'),
        ('double', 'Double'),
        ('suite', 'Suite')
    ], string='Room Type')
    price = fields.Float('Price')
    weekend_price = fields.Float('Weekend Price')
    is_weekend = fields.Boolean('Is Weekend', compute='_compute_is_weekend', store=True)

    @api.depends('date')
    def _compute_is_weekend(self):
        for record in self:
            if record.date:
                weekday = record.date.weekday()
                record.is_weekend = weekday >= 5  # 5 = Saturday, 6 = Sunday

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                WITH RECURSIVE dates AS (
                    SELECT current_date AS date
                    UNION ALL
                    SELECT date + 1
                    FROM dates
                    WHERE date < current_date + interval '30 days'
                )
                SELECT
                    row_number() OVER () AS id,
                    d.date AS date,
                    r.id AS room_id,
                    CASE
                        WHEN b.state = 'confirmed' AND d.date BETWEEN b.check_in AND b.check_out THEN 'booked'
                        WHEN b.state = 'checkin' AND d.date BETWEEN b.check_in AND b.check_out THEN 'booked'
                        WHEN r.state = 'maintenance' THEN 'maintenance'
                        WHEN r.state = 'reserved' THEN 'reserved'
                        ELSE 'available'
                    END AS state,
                    r.hotel_id AS hotel_id,
                    r.bed_type AS bed_type,
                    r.price AS price,
                    r.weekend_price AS weekend_price
                FROM dates d
                CROSS JOIN hotel_room r
                LEFT JOIN hotel_booking b ON b.room_id = r.id
                    AND b.state in ('confirmed', 'checkin')
                    AND d.date BETWEEN b.check_in AND b.check_out
            )
        """ % self._table)