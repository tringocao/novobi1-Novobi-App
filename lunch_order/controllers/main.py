# -*- coding: utf-8 -*-
from odoo import http, api
import random
from datetime import datetime
from datetime import timedelta
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.auth_signup.models.res_users import SignupError

from odoo.addons.web.controllers.main import Home
from odoo.http import request
from odoo.exceptions import UserError
import json
import logging
from werkzeug.exceptions import Forbidden
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
from odoo.http import request
from odoo.addons.base.ir.ir_qweb.fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
# from odoo.addons.website_sale.controllers.main import TableCompute

from odoo.exceptions import ValidationError
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.addons.portal.controllers.portal import *

import logging

_logger = logging.getLogger(__name__)

email_admin = '1513636@hcmut.edu.vn'
PPG = 20  # Products Per Page
PPR = 4   # Products Per Row
class TableCompute(object):

    def __init__(self):
        self.table = {}

    def _check_place(self, posx, posy, sizex, sizey):
        res = True
        for y in range(sizey):
            for x in range(sizex):
                if posx + x >= PPR:
                    res = False
                    break
                row = self.table.setdefault(posy + y, {})
                if row.setdefault(posx + x) is not None:
                    res = False
                    break
            for x in range(PPR):
                self.table[posy + y].setdefault(x, None)
        return res

    def process(self, products, ppg=PPG):
        # Compute products positions on the grid
        minpos = 0
        index = 0
        maxy = 0
        x = 0
        for p in products:
            x = min(max(1, 1), PPR)
            y = min(max(1, 1), PPR)
            if index >= ppg:
                x = y = 1

            pos = minpos
            while not self._check_place(pos % PPR, pos // PPR, x, y):
                pos += 1
            # if 21st products (index 20) and the last line is full (PPR products in it), break
            # (pos + 1.0) / PPR is the line where the product would be inserted
            # maxy is the number of existing lines
            # + 1.0 is because pos begins at 0, thus pos 20 is actually the 21st block
            # and to force python to not round the division operation
            if index >= ppg and ((pos + 1.0) // PPR) > maxy:
                break

            if x == 1 and y == 1:   # simple heuristic for CPU optimization
                minpos = pos // PPR

            for y2 in range(y):
                for x2 in range(x):
                    self.table[(pos // PPR) + y2][(pos % PPR) + x2] = False
            self.table[pos // PPR][pos % PPR] = {
                'product': p, 'x': x, 'y': y,
                # 'class': " ".join(x.html_class for x in p.website_style_ids if x.html_class)
            }
            if index <= ppg:
                maxy = max(maxy, y + (pos // PPR))
            index += 1

        # Format table according to HTML needs
        rows = sorted(self.table.items())
        rows = [r[1] for r in rows]
        for col in range(len(rows)):
            cols = sorted(rows[col].items())
            x += len(cols)
            rows[col] = [r[1] for r in cols if r[1]]

        return rows

class Restaurant(object):
    _schema = {
        'RestaurantName': '',
        'RestaurantAddress': '',
        'ImageUrl': '',
        'DetailUrl': '',
        'PromotionTitle': ''
    }

    def __init__(self, data):
        self.data = dict((key, data[key]) for key in list(self._schema.keys()))

    def print_all(self):
        for e in self.data:
            print (self.data[e])

class Item(object):
    _schema = {
        'name': '',
        'price': '',
        'image': '',
        'rating': '',
    }

    def __init__(self, data):
        self.data = dict((key, data[key]) for key in list(self._schema.keys()))

    def print_all(self):
        for e in self.data:
            print (self.data[e])


class LunchController(WebsiteSale):
    @http.route(['/lunch/confirm'], type='http', auth="user", website=True)
    def lunch_confirm(self,**post):

        sale_order_id = request.session.get('lunch_order_id')
        if sale_order_id:
            order = request.env['lunch.order'].sudo().browse(sale_order_id)
            return request.render("lunch_order.lunch_confirm_view", {'order': order, 'here':'lunch'})
        else:
            return request.redirect('/lunch')

    @http.route(['/foody/<string:a>/<string:b>/confirm'], type='http', auth="user", website=True)
    def foody_confirm(self,**post):

        sale_order_id = request.session.get('lunch_order_id')
        if sale_order_id:
            order = request.env['lunch.order'].sudo().browse(sale_order_id)
            return request.render("lunch_order.lunch_confirm_view", {'order': order,'here':'foody'})
        else:
            return request.redirect('/foody')


    @http.route(['/lunch/page/<int:page>', '/lunch'], type='http', auth="user", website=True)
    def lunch_page(self,page=0, category=None, search='', ppg=False, **post):
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG


        keep = QueryURL('/lunch', category=category and int(category), search=search, attrib=None, order=post.get('order'))

        compute_currency, pricelist_context, pricelist = self._get_compute_currency_and_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/lunch"
        if search:
            post["search"] = search

        now = datetime.now().strftime("%A")
        Product_menu=request.env['lunch.menu'].sudo().search([('name', '=', now)])
        Product = request.env['lunch.product'].sudo()

        parent_category_ids = []

        product_count = Product.search_count([('id','in',Product_menu.product_in_day.ids)])
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        products = Product.search([('id','in',Product_menu.product_in_day.ids)], limit=ppg, offset=pager['offset'], order=None)

        values = {
            'search': search,
            'category': category,
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg),
            'rows': PPR,
            'compute_currency': compute_currency,
            'keep': keep,
            'parent_category_ids': parent_category_ids,
            'onhome': True
        }
        if category:
            values['main_object'] = category

        return request.render("lunch_order.lunch_home", values)

    @http.route(['/autoOrder'], type='json', website=True, auth="user", csrf=False)
    def autoOrder(self, **post):
        if not post.get('imgurl'):
            id = post.get('item_id')
            order = request.website.sale_get_lunch_order(force_create=1,product_id= id)

        else:
            imgurl = None
            if post.get('imgurl') != "/content/images/no-image.png":
                imgurl = post.get('imgurl')
            name = post.get('name')
            price = post.get('price')
            product_id = request.env.ref('lunch_order.product_product_21').id
            order = request.website.sale_get_lunch_order(force_create=1,product_id= product_id, tuple=(name,imgurl,price))

        result = {}
        result['lunch_order.cart_review'] = request.env['ir.ui.view'].render_template('lunch_order.cart_review', {
            'order_line_id': order,
        })

        return result
    @http.route(['/deltproduct'], type='json', website=True, auth="user", csrf=False)
    def deltproduct(self,**post):
        item_id = request.env['lunch.order.line'].sudo().search([('id', '=', post.get("item_id"))]).unlink()
        order = request.website.sale_get_lunch_order()
        result = {}
        result['lunch_order.lunch_cart_review_body'] = request.env['ir.ui.view'].render_template('lunch_order.lunch_cart_review_body', {
            'order_line_id': order,
        })

        return result
    @http.route(['/confirmorder'], type='json', website=True, auth="user", csrf=False)
    def confirmproduct(self,**post):
        item_id = request.env['lunch.order'].sudo().search([('id', '=', post.get("item_id"))])
        results = item_id.sudo().write({'state': 'confirmed'})
        partner = request.env.user.partner_id
        partner.sudo().write({'last_lunch_order_id': None})

        for item in item_id.order_line_ids:
            item.sudo().write({'state': 'confirmed'})
        request.session['lunch_order_id'] = False
        _logger.info("in confirmproductttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt")
        _logger.info(request.session['lunch_order_id'])

        return True

    @http.route(['/receive_slack '], type='json', website=True, auth="user",methods=['POST'], csrf=False)
    def receive_slack(self,**post):
        if post.get('token') == "NrE1wTcTzSZ5S6plNPBexrIt":
            channel = post.get('channel')
            username = post.get('username')
            return "Channel: " + channel + "Username: " + username
        else:
            return "None found"

    @http.route(['/foody'], type='http', auth="user", website=True)
    def lunch_page_foody(self, page=0, category=None, search='', ppg=False, **post):
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG



        keep = QueryURL('/foody', category=category and int(category), search=search, attrib=None,
                        order=post.get('order'))

        compute_currency, pricelist_context, pricelist = self._get_compute_currency_and_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)
        product_count = 0
        products = []
        url = "/foody"
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)

        if search:
            quote_page = 'https://www.now.vn/ho-chi-minh/food/danh-sach-dia-diem-giao-tan-noi?q=' + search.replace(' ','+')
            page = urlopen(quote_page)
            soup = BeautifulSoup(page, 'html.parser')
            datas = soup.find_all('script')
            for data in datas:
                text = data.text
                if "ListResult" in text:
                    start = text.index('var model =')
                    end = text.find("};", start)
                    temp = text[start:end + 1].replace('var model =', '').strip()
                    list_restaurants = json.loads(temp).get('ListResult', [])
                    response = []
                    for r in list_restaurants:
                        response.append(Restaurant(r))


            pager = request.website.pager(url=url, total=1, page=page, step=ppg, scope=7, url_args=post)
            products = response


        values = {
            'search': search,
            'category': category,
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg),
            'rows': PPR,
            'compute_currency': compute_currency,
            'keep': keep,
            'parent_category_ids': [],
            'onhome': True
        }
        if category:
            values['main_object'] = category

        return request.render("lunch_order.foody_home", values)



    @http.route(['/foody/ho-chi-minh/<string:name_product>'], type='http', auth="user", website=True)
    def lunch_page_foody_product(self, name_product, **post):
        detail_page = 'https://www.now.vn/ho-chi-minh/'+name_product
        page = urlopen(detail_page)
        soup = BeautifulSoup(page, 'html.parser')
        items = soup.find_all("div", attrs={"class": "menu-group"})
        images = soup.find("img", attrs={"alt": name_product})
        if images:
            images=images.attrs['src']
        response = {}
        for item in items:
            datas = item.find_all("div", attrs={"class": "list-menu"})
            group_name = item.find("div", attrs={"class": "title-menu"}).text.strip()
            response[group_name] = []
            for data in datas:
                name = data.find("div", attrs={"class": "item-restaurant-name"}).text.strip()
                price = data.find("div", attrs={"class": "current-price"}).text.strip().replace('\n', ' ')
                image = data.find("img")['src']
                rating = data.find("p").find_all("span")
                rating = ' '.join(x.text for x in rating[0:1])
                value = {
                    'name': name,
                    'price': price,
                    'image': image,
                    'rating': rating,
                }
                if not images:
                    images = image
                response[group_name].append(Item(value))

        values ={
            'images': images,
            'bins':response,
            'onhome':True
        }
        return request.render("lunch_order.foody_product_home", values)

class SignUpSlack(AuthSignupHome):

    def _signup_with_values(self, token, values):
        values.update({
            'slack_name':request.params.get('slack_name')
        })
        return super(SignUpSlack, self)._signup_with_values(token, values)

