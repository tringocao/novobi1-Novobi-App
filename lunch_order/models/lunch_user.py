from odoo import api, fields, models
from time import gmtime, strftime
import requests
import json

class DemoUserScheduler(models.Model):
    _inherit = 'res.users' #id = 379?
    slack_name = fields.Char(string="Slack Name", required=False, default="noname")
    @api.model
    def sent_message(self, message):
        url = "https://hooks.slack.com/services/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"
        payload = {"text":  message}
        r = requests.post(url, data=json.dumps(payload))
        return True

    @api.model
    def sent_detail_message(self, message):
        # maybe error
        users = self.env['lunch.order'].sudo().search([('state', '=', 'confirmed'),('date.','=',strftime("%Y-%m-%d", gmtime()))])
        list_id =[]
        for user in users:
            list_id.append(user.user_id.id)
        if users:
            users_no_order = self.env['res.users'].sudo().search([('id', 'not in', list_id)])
        users_no_order_name = ""
        for user in users_no_order:
            users_no_order_name += user.slack_name + " "
        url = "https://hooks.slack.com/services/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"
        payload = {
            "text": "Are you hungry?" + users_no_order_name}
        r = requests.post(url, data=json.dumps(payload))
        return True

class LunchPartner(models.Model):
        _inherit = 'res.partner'

        last_lunch_order_id = fields.Many2one('lunch.order', string='Last Online Lunch Order')
