/** @odoo-module **/

import { registry } from '@web/core/registry';
import { Layout } from '@web/search/layout';
import { getDefaultConfig } from "@web/views/view";
import { Component, onWillStart, onMounted } from "@odoo/owl";

class RoomDashboard extends Component {
    setup() {
        super.setup();
        onWillStart(async () => {
            await this.fetchDashboardData();
        });

        onMounted(() => {
            this.renderCharts();
        });
    }

    async fetchDashboardData() {
        try {
            const result = await this.env.services.rpc({
                route: '/api/room_dashboard/data',
                params: {},
            });
            if (result.status === 'success') {
                this.state.data = result.data;
            }
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
        }
    }

    renderCharts() {
        // Add chart rendering logic here if needed
    }
}

RoomDashboard.template = 'Hotel_Management.RoomDashboard';
RoomDashboard.components = { Layout };
RoomDashboard.defaultProps = {
    ...getDefaultConfig(),
};

// Thay đổi key trong registry để khớp với tag trong action
registry.category('actions').add('hotel_management.room_dashboard', RoomDashboard);