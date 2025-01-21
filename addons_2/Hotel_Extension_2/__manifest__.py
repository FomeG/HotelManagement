{
    'name': "Hotel_Extension_2",
    'summary': "Extension for Hotel Management with additional features",
    'description': """
        This module extends Hotel Management with:
        - Automatic night calculation
        - Extended booking workflow 
        - Hotel services management
        - Integration with Sales module
    """,
    'author': "Your Company",
    'website': "https://www.yourcompany.com",
    'category': 'Services',
    'version': '0.1',
    'depends': ['Hotel_Management', 'sale', 'product','web','stock'],
    'data': [
        'reports/hotel_booking_report_template.xml',
        
        'security/ir.model.access.csv',
        'views/hotel_booking_views.xml',
        'views/hotel_service_views.xml',
        'views/room_extend_views.xml',
        'views/hotel_service_inventory_views.xml',
        
        'data/cronjob.xml',
        
    ],
}