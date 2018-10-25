from odoo import api, fields, models
import base64
from time import gmtime, strftime
import requests
import json
from datetime import datetime, timedelta
from odoo.http import request
from odoo.addons import decimal_precision as dp
import datetime

my_api_key = "AIzaSyAP8YBUJY75YmtcFmeR6tHmfSKzVgn6MA0"
my_cse_id = "002299992021745164164:xkjeivdgypq"


class Foods(models.Model):
    _name = 'lunch_order.foods'
    name = fields.Char(string="Food Name", required=False, )
    src = fields.Char(string="Food Img", required=False, )


class LunchMenu(models.Model):
    _name = "lunch.menu"
    name = fields.Selection([('Monday', 'Monday'),
                             ('Tuesday', 'Tuesday'),
                             ('Wednesday', 'Wednesday'),
                             ('Thursday', 'Thursday'),
                             ('Friday', 'Friday'),
                             ('Saturday', 'Saturday'),
                             ('Sunday', 'Sunday')],
                            'Day', )
    product_in_day = fields.Many2many(comodel_name="lunch.product", string="Product in this day", required=False, )


class Lunchs(models.Model):
    _inherit = "lunch.product"

    img = fields.Binary(required=False, )

    @api.multi
    def google_search(self):
        # srcImg
        url = "https://www.googleapis.com/customsearch/v1?key=" + my_api_key + "&cx=" + my_cse_id + "&searchType=image&q=" + self.name
        response = requests.get(url)
        # datas = None
        # with response as f:
        data = json.loads(response.content.decode('utf-8'))
        items = list(data.get('items'))

        return {
            'name': 'Image Options',
            'tag': 'lunch_order.img',
            'context': {
                'items': items,
            },
            'target': 'new',
            'type': 'ir.actions.client',
        }

    @api.model
    def update_selected_plan(self, items_id, data):
        food = self.sudo().browse(items_id)

        return food.sudo().write({
            'img': base64.b64encode(requests.get(data['link']).content)
        })


class LunchsOrder(models.Model):
    _inherit = "lunch.order.line"
    img = fields.Binary(required=False, )

    # type = fields.Selection([('foody', 'Foody'),
    #                          ('lunch', 'Lunch'),
    #                          ('other', 'Other')],
    #                         'Type', readonly=True, index=True, default='lunch')

    price = fields.Float(related=False, readonly=False, store=True, default='product_id.price',
                         digits=dp.get_precision('Account'))


class SchedulerLunch(models.Model):
    _inherit = 'lunch.alert'
    announce_time = fields.Datetime(string="Start", required=False, )
    func_type = fields.Selection([('sent_message', 'Call all'),
                                  ('sent_detail_message', 'Call detail')])

    @api.model
    def createSchedule(self, start_, unit, num_times, start, interval_number, name_method, model_id):
        code = 'model.' + name_method[1] + '("{}")'.format(name_method[2])
        value = {
            'name': start_,
            'model_id': model_id,  # id of model scheduler.demo is 379
            'numbercall': num_times,
            'interval_number': interval_number,
            'interval_type': unit,
            'nextcall': start,
            'user_id': 1,
            'doall': False,
            'priority': 5,
            'active': True,
            'state': 'code',
            'code': code,

            # 'model': 'scheduler.demo',
            # 'function': 'createSaleOrder(old_order_id)',
        }
        sudocron = self.env['ir.cron'].sudo()
        res = sudocron.create(value)
        return res

    @api.multi
    def start_scheduler(self):
        unit = 'days'
        num_times = -1
        futuredate = datetime.now() + timedelta(minutes=1)
        start_ = futuredate.strftime("%Y-%m-%d %H:%M:%S")
        interval_number = 1  # 1 day
        cron_id_active = self.env['ir.cron'].sudo().search([('name', '=', start_)])
        cron_id_inactive = self.env['ir.cron'].sudo().search(
            [('name', '=', start_),
             ('active', '=', False)])

        cron_id = cron_id_inactive or cron_id_active
        vals = {}

        if (not cron_id_inactive) and (not cron_id_active):
            res = self.createSchedule(start_, unit, num_times, start_, interval_number,
                                      ('', 'check_time_announce', '0'), self.env.ref('lunch.model_lunch_alert').id)
        else:
            if cron_id.nextcall != start_:
                vals.update({'nextcall': start_, })
            if cron_id.interval_number != interval_number:
                vals.update({'interval_number': interval_number, })
            if cron_id.interval_type != unit:
                vals.update({'interval_type': unit, })
            if cron_id.numbercall != num_times:
                vals.update({'numbercall': num_times, })
            vals.update({'active': True})
            res = cron_id.write(vals)

        return

    # create scheduler start get data from form lunch alert
    # start at the time we press this button

    @api.model
    def announce_scheduler(self, alert):
        unit = 'days'
        num_times = 1
        start_ = alert[0]
        interval_number = 1
        code = 'model' + alert[1] + '({})'
        cron_id_active = self.env['ir.cron'].sudo().search([('code', '=', code.format(alert[2]))])
        cron_id_inactive = self.env['ir.cron'].sudo().search(
            [('code', '=', code.format(alert[2])),
             ('active', '=', False)])

        cron_id = cron_id_inactive or cron_id_active
        vals = {}

        if (not cron_id_inactive) and (not cron_id_active):
            res = self.createSchedule(start_, unit, num_times, start_, interval_number,
                                      alert, self.env.ref('base.model_res_users').id)
        else:
            if cron_id.nextcall != start_:
                vals.update({'nextcall': start_, })
            if cron_id.interval_number != interval_number:
                vals.update({'interval_number': interval_number, })
            if cron_id.interval_type != unit:
                vals.update({'interval_type': unit, })
            if cron_id.numbercall != num_times:
                vals.update({'numbercall': num_times, })
            vals.update({'active': True})
            res = cron_id.write(vals)

        return

    @api.model
    def check_time_announce(self, message):
        alert_msg = [(alert.announce_time, alert.func_type, alert.message)
                     for alert in self.env['lunch.alert'].search([])
                     if alert.display]
        for alert in alert_msg:
            self.announce_scheduler(alert)


class LunchOrderScheduler(models.Model):
    _inherit = "lunch.order"


    @api.model
    def scheduler_report(self):
        # send for admin
        num_admin = self.env['res.users'].search([('login', '=', 'admin')], limit=1)
        invite4admin = request.env.ref('lunch_order.mail_admin', raise_if_not_found=False)
        # send for admin
        invite4admin.sudo().with_context(
            email_admin=num_admin.email,
        ).send_mail(num_admin.id, force_send=True)

        # send for user
        order = self.env['lunch.order'].search([('state', '=', 'confirmed')]).filtered(
            lambda record: datetime.datetime.strptime(str(record.date), '%Y-%m-%d').month == int(
                strftime("%m", gmtime()))
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
            list_user = []
            for user in users_order:
                list_user.append(user.id)

            # because some account unactive
            if len(list_id_set) != len(list_user):
                complement_set = list((set(list_id_set) - set(list_user)))
                users_order = users_order.filtered(lambda r: r.user_id.id not in complement_set)

        for user in users_order:
            invite4User = request.env.ref('lunch_order.mail_user', raise_if_not_found=False)
            invite4User.sudo().with_context(
                email_user=user.login,
                email_admin=num_admin.email,
            ).send_mail(user.id, force_send=True)

        return True