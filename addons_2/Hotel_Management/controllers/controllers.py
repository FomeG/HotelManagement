# Add these imports at the top
from odoo import http
from odoo.http import request
import json

# Add this new controller class
class RoomDashboardController(http.Controller):
    @http.route('/api/room_dashboard/data', type='json', auth='user')
    def get_dashboard_data(self):
        try:
            # Get rooms data
            rooms = request.env['hotel.room'].search_read(
                [],  # domain
                ['name', 'state', 'hotel_id', 'bed_type', 'price', 'last_booking_date']
            )

            # Get statistics
            total_rooms = len(rooms)
            available_rooms = len([r for r in rooms if r['state'] == 'available'])
            booked_rooms = len([r for r in rooms if r['state'] == 'booked'])

            return {
                'status': 'success',
                'data': {
                    'rooms': rooms,
                    'stats': {
                        'total': total_rooms,
                        'available': available_rooms,
                        'booked': booked_rooms
                    }
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/api/room_dashboard/update_status', type='json', auth='user')
    def update_room_status(self, room_id, new_status):
        try:
            room = request.env['hotel.room'].browse(int(room_id))
            if room.exists():
                room.write({'state': new_status})
                return {
                    'status': 'success',
                    'message': f'Room {room.name} status updated to {new_status}'
                }
            return {
                'status': 'error',
                'message': 'Room not found'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }