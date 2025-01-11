# -*- coding: utf-8 -*-
{
    'name': 'Hotel Management Extension',
    'version': '1.0',
    'category': 'Services',
    'summary': 'Extension for Hotel Management module',
    'description': """
        This module extends the Hotel Management functionality with additional features:
        - Extended room information (size, max occupancy, smoking policy)
        - Booking history for hotels
        - New booking history tracking
    """,

    'author': "Trọng Nghĩa",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['Hotel_Management'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/booking_confirm_views.xml',
        'views/room_extends_views.xml',
        'views/hotel_extends_views.xml',
        'views/bookinghistory_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

