
from odoo import api, fields, models
from odoo.http import request
import base64
import requests


import logging

_logger = logging.getLogger(__name__)


class LunchWebsite(models.Model):
    _inherit = 'website'
    @api.multi
    def sale_get_lunch_order(self, force_create=False, product_id = False, tuple = None):
        """ Return a new sales order for one-click checkout process after mofications specified by params.
        :param bool force_create: Create sales order if not already existing
        :param str code: Code to force a pricelist (promo code)
                         If empty, it's a special case to reset the pricelist with the first available else the default.
        :param bool update_pricelist: Force to recompute all the lines from sales order to adapt the price with the current pricelist.
        :param int force_pricelist: pricelist_id - if set,  we change the pricelist with this one
        :returns: browse record for the current sales order
        """
        self.ensure_one()
        partner = self.env.user.partner_id

        # Ignore current cart
        sale_order_id = request.session.get('lunch_order_id')
        _logger.info(str(request.session.get(
                         'lunch_order_id', 0)) + " in sale_get_lunch_orderrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")

        if not sale_order_id:
            last_order = partner.last_lunch_order_id
            # Do not reload the cart of this user last visit if the cart is no longer draft or uses a pricelist no longer available.
            sale_order_id = last_order.state == 'new' and last_order.id

        # Test validity of the sale_order_id
        sale_order = self.env['lunch.order'].sudo().browse(sale_order_id).exists() if sale_order_id else None

        # create so if needed
        if not sale_order and force_create :
            sale_order = self.env['lunch.order'].sudo().create({
                'user_id': self.env.context.get('uid'),
                'order_line_ids': '[]',
            })


            request.session['lunch_order_id'] = sale_order.id

            partner.write({'last_lunch_order_id': sale_order.id})

        if sale_order:
            if product_id:
                item_id = self.env['lunch.product'].sudo().search([('id', '=', product_id)], limit=1)
                note = None
                price = 0
                imgurl = None
                if tuple:
                    note =tuple[0]
                    imgurl = tuple[1]
                    price = int(tuple[2])*0

                sale_order_line = self.env['lunch.order.line'].sudo().create({
                    'order_id': sale_order.id,
                    'product_id': product_id,
                    'price': price if price else item_id.price,
                    'note': note if note else item_id.name,
                    'cashmove': [],
                    'img': item_id.img if not imgurl else base64.b64encode(requests.get(imgurl).content)

                    # 'type': 'lunch',
                })
                # case when user emptied the cart
                if not request.session.get('lunch_order_id'):
                    request.session['lunch_order_id'] = sale_order.id
        else:
            request.session['lunch_order_id'] = False
            return self.env['lunch.order']

        return sale_order

