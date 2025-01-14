from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HotelBookingPaymentWizard(models.TransientModel):
    _name = 'hotel.booking.payment.wizard'
    _description = 'Hotel Booking Payment Wizard'

    booking_id = fields.Many2one('hotel.booking', string='Booking', required=True)
    hotel_id = fields.Many2one('hotel.management', string='Hotel', readonly=True)
    room_id = fields.Many2one('hotel.room', string='Room', readonly=True)
    payment_amount = fields.Float('Payment Amount', required=True)

    @api.constrains('payment_amount')
    def _check_payment_amount(self):
        for record in self:
            if record.payment_amount <= 0:
                raise ValidationError('Số tiền thanh toán phải lớn hơn 0')
            

    def action_confirm_payment(self):
        self.ensure_one()
        if self.booking_id:
            self.booking_id.write({
                'payment_status': 'paid',
                'payment_date': fields.Datetime.now(),
                'payment_amount': self.payment_amount,
            })
        return {'type': 'ir.actions.act_window_close'}