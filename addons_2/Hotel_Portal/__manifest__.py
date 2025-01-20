{
    'name': "Hotel Portal",
    'summary': "Portal interface for hotel bookings",
    'description': """
        This module provides a portal interface for:
        - Viewing available rooms
        - Making room bookings
        - Managing existing bookings
        - Ordering additional services
    """,
    'author': "Your Company",
    'website': "https://www.yourcompany.com",
    'category': 'Services',
    'version': '0.1',
    'depends': [
        'Hotel_Management',
        'Hotel_Extension_2',
        'portal',
        'website'
    ],
    'data': [
        'security/ir.model.access.csv',
        
        
        
        'views/portal_templates.xml',
        'views/website_menu.xml',
    ],
}