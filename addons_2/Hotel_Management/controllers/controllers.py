# -*- coding: utf-8 -*-
from odoo import http
import requests
from odoo.http import Controller, route, request

# class Ss34(http.Controller):
#     @http.route('/ss34/ss34', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @route('/api/get_data', type='json', auth='public', methods=['POST'])
#     def get_data(self, **kwargs):
#         # Xử lý yêu cầu từ client
#         records = request.env['your.model'].search([])
#         return {'data': records.read(['field1', 'field2'])}


#     @http.route('/ss34/ss34/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ss34.listing', {
#             'root': '/ss34/ss34',
#             'objects': http.request.env['ss34.ss34'].search([]),
#         })

#     @http.route('/ss34/ss34/objects/<model("ss34.ss34"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ss34.object', {
#             'object': obj
#         })


class APIController(http.Controller):

    @http.route('/api/get_transactions', type='http', auth='public', methods=['GET'])
    def get_transactions(self, **kw):
        # Bước 1: Gửi yêu cầu GET tới API
        api_url = "https://script.google.com/macros/s/AKfycbxDT6RNiRIexcNzU91la5dLirQMRke9Lg6Qcenj7iAUSirn6QBEH46fM99ThDxLDwyBBw/exec"
        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Kiểm tra nếu có lỗi HTTP
            data = response.json()  # Chuyển đổi từ JSON thành dict
        except requests.exceptions.RequestException as e:
            return request.make_response(
                f"Error fetching data from API: {str(e)}",
                500,
                headers={"Content-Type": "text/plain"}
            )

        # Bước 2: Kiểm tra xem API trả về lỗi hay không
        if data.get('error'):
            return request.make_response(
                "API returned an error.",
                500,
                headers={"Content-Type": "text/plain"}
            )

        # Bước 3: Xử lý dữ liệu (tùy chỉnh theo nhu cầu)
        transactions = data.get('data', [])
        processed_data = [
            {
                "transaction_id": txn["Mã GD"],
                "description": txn["Mô tả"],
                "amount": txn["Giá trị"],
                "transaction_date": txn["Ngày diễn ra"],
                "account_number": txn["Số tài khoản"]
            }
            for txn in transactions
        ]

        # Bước 4: Trả dữ liệu JSON về client
        return request.make_response(
            request.json_response({"error": False, "transactions": processed_data}),
            200,
            headers={"Content-Type": "application/json"}
        )
