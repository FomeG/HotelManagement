from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager # type: ignore
from odoo.exceptions import AccessError, MissingError
from odoo.osv.expression import OR

class HotelPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'order_count' in counters:
            values['order_count'] = request.env['sale.order'].search_count([
                ('partner_id', '=', request.env.user.partner_id.id)
            ])
        return values
    
    
    
    @http.route(['/my/hotel/service/order'], type='http', auth="user", methods=['POST'], website=True)
    def portal_order_service(self, **post):
        """Handle service ordering from portal"""
        booking_id = int(post.get('booking_id'))
        service_id = int(post.get('service_id'))
        quantity = float(post.get('quantity', 1.0))

        try:
            # Check access rights
            booking_sudo = self._document_check_access('hotel.booking', booking_id)
            
            # Create service line
            service_line = request.env['hotel.booking.service.line'].sudo().create({
                'booking_id': booking_id,
                'service_id': service_id,
                'quantity': quantity
            })
            
            return request.redirect('/my/hotel/booking/%s' % booking_id)
            
        except Exception as e:
            return request.redirect('/my/hotel/booking/%s?error=%s' % (booking_id, str(e)))


    @http.route(['/my/orders', '/my/orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        
        orders = request.env['sale.order'].search([
            ('partner_id', '=', request.env.user.partner_id.id)
        ])
        
        values.update({
            'orders': orders,
            'page_name': 'order',
        })
        return request.render("Hotel_Extension_2.portal_my_orders", values)
    
    def _get_search_domain(self, search_in, search):
        domain = []
        if search_in in ('all', 'name'):
            domain = OR([domain, [('name', 'ilike', search)]])
        return domain

    @http.route(['/my/hotel/bookings', '/my/hotel/bookings/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_hotel_bookings(self, page=1, sortby=None, filterby=None, search=None, search_in='all', **kw):
        values = self._prepare_portal_layout_values()
        
        domain = []
        if search:
            domain += self._get_search_domain(search_in, search)

        searchbar_sortings = {
            'date': {'label': _('Booking Date'), 'order': 'booking_date desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'state': {'label': _('Status'), 'order': 'state'},
        }

        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Count for pager
        booking_count = request.env['hotel.booking'].search_count(domain)

        # Pager
        pager = portal_pager(
            url="/my/hotel/bookings",
            url_args={'sortby': sortby},
            total=booking_count,
            page=page,
            step=self._items_per_page
        )

        # Content
        bookings = request.env['hotel.booking'].search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )

        values.update({
            'bookings': bookings,
            'page_name': 'hotel_booking',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'default_url': '/my/hotel/bookings',
        })
        return request.render("Hotel_Portal.portal_my_hotel_bookings", values)

    @http.route(['/my/hotel/booking/<int:booking_id>'], type='http', auth="user", website=True)
    def portal_my_hotel_booking(self, booking_id=None, **kw):
        try:
            booking_sudo = self._document_check_access('hotel.booking', booking_id)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = {
            'page_name': 'hotel_booking',
            'booking': booking_sudo,
        }
        return request.render("Hotel_Portal.portal_my_hotel_booking", values)

    @http.route(['/hotel/rooms'], type='http', auth="public", website=True)
    def hotel_rooms(self, **kw):
        available_rooms = request.env['hotel.room'].sudo().search([
            ('state', '=', 'available')
        ])
        values = {
            'rooms': available_rooms,
            'page_name': 'hotel_rooms',
        }
        return request.render("Hotel_Portal.hotel_rooms", values)

    @http.route(['/hotel/book'], type='http', auth="user", website=True)
    def book_room(self, **post):
        if post and request.httprequest.method == 'POST':
            # Get room and its type
            room = request.env['hotel.room'].sudo().browse(int(post.get('room_id')))

            vals = {
                'name': f"Web Booking - {room.name}",
                'customer_name': request.env.user.partner_id.id,
                'room_type': room.bed_type,
                'hotel_id': room.hotel_id.id,
                'room_id': room.id,
                'check_in': post.get('check_in'),
                'check_out': post.get('check_out'),
                'state': 'draft'
            }
            booking = request.env['hotel.booking'].sudo().create(vals)
            return request.redirect(f'/my/hotel/booking/{booking.id}')

        # Load available rooms
        rooms = request.env['hotel.room'].sudo().search([('state', '=', 'available')])
        values = {
            'rooms': rooms,
            'page_name': 'book_room'
        }
        return request.render("Hotel_Portal.hotel_book_form", values)
    
    
    
    
    
    @http.route(['/my/hotel/services/<int:booking_id>'], type='http', auth="user", website=True)
    def portal_my_services(self, booking_id=None, **kw):
        try:
            booking_sudo = self._document_check_access('hotel.booking', booking_id)
        except (AccessError, MissingError):
            return request.redirect('/my')
            
        # Get available services
        services = request.env['hotel.service'].sudo().search([])
        
        values = {
            'page_name': 'hotel_services',
            'booking': booking_sudo,
            'services': services
        }
        return request.render("Hotel_Portal.portal_my_services", values)

    @http.route(['/hotel/order_service'], type='json', auth="user", website=True)
    def order_service(self, service_id, **kw):
        service = request.env['hotel.service'].browse(int(service_id))
        
        # Create sale order
        order_vals = {
            'partner_id': request.env.user.partner_id.id,
            'order_line': [(0, 0, {
                'product_id': service.product_tmpl_id.product_variant_id.id,
                'name': service.name,
                'product_uom_qty': 1,
                'price_unit': service.price,
            })]
        }
        
        order = request.env['sale.order'].sudo().create(order_vals)
        
        return {
            'success': True,
            'order_id': order.id
        }
    
    
    
    
    @http.route(['/my/services'], type='http', auth="user", website=True)
    def portal_services(self, **kw):
        values = self._prepare_portal_layout_values()
        
        services = request.env['hotel.service'].search([])
        values.update({
            'services': services,
            'page_name': 'services'
        })
        return request.render("Hotel_Extension_2.portal_services", values)