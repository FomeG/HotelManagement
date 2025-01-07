# -*- coding: utf-8 -*-
{
    'name': "Hotel Management (SS3_4)",

    'summary': "Hotel Management System",

    'description': """
Hotel management system with room management functionality
    """,

    'author': "AHT TECH",
    'website': "https://phomeanhoa.online",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Services/Hotel',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mail'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/rules.xml',
        'security/ir.model.access.csv',
        'views/report_action.xml',
        
        'views/hotel_views.xml',
        'views/room_views.xml',
        'views/feature_views.xml',
        'views/booking_views.xml',
        
        
        'report/hotel_report_template.xml'
        
        
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    
    'installable': True,
    'application': True,
}
