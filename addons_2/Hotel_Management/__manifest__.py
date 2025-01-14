# -*- coding: utf-8 -*-
{
    'name': "Hotel Management (SS3_4)",

    'summary': "Hotel Management System",

    'description': """
Hotel management system with room management functionality
    """,

    'author': "AHT TECH",
    'website': "https://phomeanhoa.online",
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Services/Hotel',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail','hr', 'web'],

    # always loaded
    'data': [
        
        'security/security_3.xml',
        'security/rules_2.xml',
        'security/ir.model.access.csv',
        
        'views/report_action.xml',
        'views/hotel_views.xml',
        'views/room_views.xml',
        'views/feature_views.xml',
        'views/booking_views.xml',
        'views/booking_pending.xml',
        'views/templates.xml',
        
        'views/menus.xml',
        
        'wizard/hotel_booking_payment_wizard_view.xml',
        
        'reports/hotel_report_template.xml',
        'reports/hotel_detailed_report_template.xml',
        
        'data/email_config.xml',
        'data/email_template.xml',
        'data/cronjob.xml',
        'data/server_action.xml',
        
        
    ],
    
    'assets': {
        'web.assets_backend': [
            'Hotel_Management/static/src/main.js',
            'Hotel_Management/static/src/components/room_dashboard/room_dashboard.js',
            'Hotel_Management/static/src/components/room_dashboard/room_dashboard.scss',
        ],
        'web.assets_qweb': [
            'Hotel_Management/static/src/components/room_dashboard/room_dashboard.xml',
        ],
    },
    
    
    # only loaded in demonstration mode
    'demo': [],
    
    'installable': True,
    'application': True,
}
