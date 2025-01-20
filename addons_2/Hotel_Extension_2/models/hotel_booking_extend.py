from odoo import _, models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo.exceptions import ValidationError
from odoo.http import timedelta


class HotelBookingExtend(models.Model):
    _inherit = ['hotel.booking', 'portal.mixin']
    _name = 'hotel.booking'

    state = fields.Selection(selection_add=[
        ('checkin', 'Checked In'),
        ('checkout', 'Checked Out'),
        ('cancel', 'Cancelled')
    ], ondelete={'checkin': 'set default', 'checkout': 'set default', 'cancel': 'set default'})

    nights = fields.Integer('Number of Nights', compute='_compute_nights', store=True)
    total_room_price = fields.Float('Total Room Price', compute='_compute_total_room_price', store=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    
    sale_order_line_ids = fields.One2many(related='sale_order_id.order_line', string='Sale Order Lines', readonly=True)
    # Extra services for room
    service_line_ids = fields.One2many('hotel.booking.service.line', 'booking_id', string='Services')

    @api.depends('check_in', 'check_out')
    def _compute_nights(self):
        # Ez math: checkout - checkin = total nights
        for booking in self:
            if booking.check_in and booking.check_out:
                delta = booking.check_out - booking.check_in
                booking.nights = delta.days
            else:
                booking.nights = 0
                
                
    
    @api.depends('check_in', 'check_out', 'room_id')
    def _compute_total_price(self):
        for booking in self:
            total = 0
            current_date = booking.check_in
            while current_date < booking.check_out:
                # Weekend price for Saturday and Sunday
                if current_date.weekday() >= 5:
                    total += booking.room_id.weekend_price
                else:
                    total += booking.room_id.price
                current_date += timedelta(days=1)
            booking.total_room_price = total
            
            
            

    @api.model
    def _prepare_service_sale_line(self, service_line):
        """Prepare sale order line values for a service line"""
        return {
            'product_id': service_line.service_id.product_tmpl_id.product_variant_id.id,
            'name': service_line.service_id.name,
            'product_uom_qty': service_line.quantity,
            'price_unit': service_line.price_unit,
        }
        
    @api.depends('room_id.price', 'nights')
    def _compute_total_room_price(self):
        for booking in self:
            booking.total_room_price = booking.room_id.price * booking.nights if booking.room_id and booking.nights else 0.0
        
        
    @api.model 
    def create(self, vals):
        res = super().create(vals)
        if vals.get('service_line_ids'):
            res._sync_services_to_sale_order()
        return res
    
    #region WORK_FLOW================================================
    def action_confirm(self):
        # When confirm booking -> create sale order and set room to reserved
        res = super(HotelBookingExtend, self).action_confirm()
        self._create_sale_order()
        self.room_id.write({'state': 'reserved'})
        return res
    
    
    
    def action_checkin(self):
        """Check in guest and mark room as booked"""
        for booking in self:
            booking.write({'state': 'checkin'})
            booking.room_id.write({'state': 'booked'})
        return True

    def action_checkout(self):
        """Check out guest and mark room as available"""
        for booking in self:
            if booking.sale_order_id and booking.sale_order_id.state in ['draft', 'sent']:
                booking.sale_order_id.action_confirm()
            booking.write({'state': 'checkout'})
            booking.room_id.write({'state': 'available'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'target': 'current',
        }

    def action_cancel(self):
        # Cancel both booking and sale order
        res = super(HotelBookingExtend, self).action_cancel()
        for booking in self:
            if booking.sale_order_id and booking.sale_order_id.state not in ['cancel']:
                booking.sale_order_id.action_cancel()
            booking.room_id.write({'state': 'available'})
        return res
    
    
    #endregion
    
    def write(self, vals):
        res = super().write(vals)
        if 'service_line_ids' in vals:
            self._sync_services_to_sale_order()
        return res

    def _create_sale_order(self):
        """Create sale order when booking is confirmed"""
        SaleOrder = self.env['sale.order']
        for booking in self:
            # Main info for sale order
            order_vals = {
                'partner_id': booking.customer_name.id,
                'date_order': fields.Datetime.now(),
                'order_line': [(0, 0, {
                    'product_id': booking.room_id.product_id.id,
                    'name': f"From: {booking.check_in} to {booking.check_out}",
                    'product_uom_qty': 1,
                    'price_unit': booking.room_id.price * booking.nights,
                })]
            }
            
            # Add extra services if any
            if booking.service_line_ids:
                for service_line in booking.service_line_ids:
                    order_vals['order_line'].append((0, 0, {
                        'product_id': service_line.service_id.product_tmpl_id.product_variant_id.id,
                        'name': service_line.service_id.name,
                        'product_uom_qty': service_line.quantity,
                        'price_unit': service_line.price_unit,
                    }))
                    
            # Create and link sale order
            sale_order = SaleOrder.create(order_vals)
            booking.sale_order_id = sale_order.id
            
            
    
    
    def action_view_sale(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'target': 'current',
        }
        
        
                    
    def _sync_services_to_sale_order(self):
        """Sync services to sale order lines"""
        for booking in self:
            if booking.sale_order_id and booking.sale_order_id.state in ['draft', 'sent']:
                # Remove existing service lines
                if booking.room_id.product_id:
                    service_lines = booking.sale_order_id.order_line.filtered(
                        lambda l: l.product_id.id != booking.room_id.product_id.id
                    )
                else:
                    service_lines = booking.sale_order_id.order_line
                service_lines.unlink()
                
                # Create new service lines
                for service_line in booking.service_line_ids:
                    self.env['sale.order.line'].create({
                        'order_id': booking.sale_order_id.id,
                        'product_id': service_line.service_id.product_tmpl_id.product_variant_id.id,
                        'name': service_line.service_id.name,
                        'product_uom_qty': service_line.quantity,
                        'price_unit': service_line.price_unit,
                    })
                    
                    
                    

    def _compute_access_url(self):
        super()._compute_access_url()
        for booking in self:
            booking.access_url = f'/my/hotel/booking/{booking.id}'

    def preview_booking(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }
        
        
        
    