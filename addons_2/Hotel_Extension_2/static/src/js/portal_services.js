odoo.define('Hotel_Extension_2.portal_services', function (require) {
    'use strict';

    function orderService(btn) {
        var serviceId = $(btn).data('service-id');
        
        // Call controller to create sale order
        $.ajax({
            url: '/hotel/order_service',
            type: 'POST',
            data: {
                service_id: serviceId,
            },
            success: function(result) {
                if (result.success) {
                    window.location = '/my/orders/' + result.order_id;
                }
            },
        });
    }

    // Make function available globally
    window.orderService = orderService;
});