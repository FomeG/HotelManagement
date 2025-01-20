/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RoomDashboard extends Component {
    static template = "Hotel_Management.RoomDashboard";
    static props = {
        hotelId: { type: Number },
    };
    
    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.notification = useService("notification");
        
        this.state = useState({
            rooms: [],
            loading: true,
            filter: 'all' 
        });
        
        this.loadRooms();
    }

    async loadRooms() {
        this.state.loading = true;
        try {
            this.state.rooms = await this.orm.searchRead(
                'hotel.room',
                [['hotel_id', '=', this.props.hotelId]], 
                ['name', 'state', 'bed_type', 'price', 'last_booking_date']
            );
        } catch (error) {
            this.notification.add(this.env._t("Failed to load rooms"), {
                type: 'danger',
            });
            console.error('Failed to load rooms:', error);
        }
        this.state.loading = false;
    }

    get filteredRooms() {
        if (this.state.filter === 'all') return this.state.rooms;
        return this.state.rooms.filter(room => room.state === this.state.filter);
    }

    setFilter(filter) {
        this.state.filter = filter;
    }

    getRoomClass(room) {
        return {
            'room-card': true,
            'room-available': room.state === 'available',
            'room-booked': room.state === 'booked'
        };
    }

    async onRoomClick(roomId) {
        await this.actionService.doAction({
            type: 'ir.actions.act_window',
            res_model: 'hotel.room',
            res_id: roomId,
            views: [[false, 'form']],
            target: 'current',
        });
    }
}

// Đăng ký component như một widget
registry.category("view_widgets").add("room_dashboard", {
    component: RoomDashboard,
});