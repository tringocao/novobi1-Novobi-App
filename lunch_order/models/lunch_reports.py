from odoo import api, models
from time import gmtime, strftime
import datetime
from functools import reduce
from collections import Counter

class LunchReportManager(models.AbstractModel):
    _name = 'report.lunch_order.report_lunchrder_manager'

    @api.model
    def get_report_values(self, docids, data=None):
        order = self.env['lunch.order'].search([('state', '=', 'confirmed')]).filtered(
            lambda record: datetime.datetime.strptime(str(record.date), '%Y-%m-%d').month == int(strftime("%m", gmtime()))
                           and datetime.datetime.strptime(str(record.date), '%Y-%m-%d').year == int(strftime("%Y",
                                                                                                         gmtime())))
        list_id = []
        # total = []
        users_order = []
        # first_user = 0
        for user in order:
            list_id.append(user.user_id.id)

        list_id_set = list(set(list_id))

        if order:
            users_order = self.env['res.users'].sudo().search([('id', 'in', list_id_set)])
            list_user =[]
            for user in users_order:
                list_user.append(user.id)

            # because some account unactive
            if len(list_id_set) != len(list_user):
                complement_set = list((set(list_id_set) - set(list_user)))
                users_order = users_order.filtered(lambda r:r.user_id.id not in complement_set)
                list_id_set = list((set(list_id_set) & set(list_user)))

        total_users_order_price = []
        total_price = 0

        for user in users_order:
            order_id = order.filtered(lambda r:r.user_id.id == int(user.id)).mapped(lambda r:r.total)
            price_id = reduce((lambda x, y: x + y), order_id)
            total_users_order_price.append(price_id)
            total_price += price_id

        docs = list(zip(users_order, total_users_order_price))

        return {
            'doc_ids': 0,
            'doc_model': 'lunch.order',
            'docs': docs,
            'total_price':total_price
        }


class LunchReportUser(models.AbstractModel):
    _name = 'report.lunch_order.report_lunchrder_user'

    @api.model
    def get_report_values(self, docids, data=None):
        # find order
        order = self.env['lunch.order'].search([('user_id', 'in', docids)]).filtered(
            lambda record: datetime.datetime.strptime(str(record.date), '%Y-%m-%d').month == int(strftime("%m", gmtime()))
                           and datetime.datetime.strptime(str(record.date), '%Y-%m-%d').year == int(strftime("%Y",
                                                                                                         gmtime())))

        user = self.env['res.users'].search([('id', 'in', docids)])

        total_price = 0
        for ord in order:
            total_price += ord.total

        return {
            'doc_ids': docids,
            'doc_model': 'lunch.order',
            'docs': order,
            'total_price': total_price,
            'user_infor': user
        }
