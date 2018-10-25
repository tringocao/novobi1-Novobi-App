odoo.define('lunch_order.ConfirmOrder', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var Dialog = require("web.Dialog");
    var Widget = require("web.Widget");
    var rpc = require("web.rpc");
    var _t = core._t;

    var RemoveOrderWidget = Widget.extend({
        events: {
            'click .btnremove': 'onBtnRemove',
        },
        init: function (parent, options) {
            this._super(parent, options);
        },
        start: function () {
            this._super();
        },
        onBtnRemove: function (ev) {
            var self = this;
            var item_id = $(ev.currentTarget).data('id');
            ajax.jsonRpc("/deltproduct", 'call', {
                'item_id': item_id,
            }).then(function (data) {
                self.$el.find("#showproduct").empty().append(data['lunch_order.lunch_cart_review_body']);

            });
        }
    })

    var ConfirmOrderWidget = Widget.extend({
        events: {
            'click .orderbtn': 'onBtnAuto',
            'click .btnfoodypro': 'onBtnFoody',
        },
        init: function (parent, id, imgurl,price) {
            this._super(parent);
            this.parent = parent;
            this.id = id;
            this.imgurl = imgurl;
            this.price = price;
        },
        onBtnAuto: function (ev) {
            var item_id = this.id
            var self = this;
            ajax.jsonRpc("/autoOrder", 'call', {
                'item_id': item_id,
            }).then(function (data) {
                self.$el.find("#place_modal").empty().append(data['lunch_order.cart_review']);
                self.$el.find("#cart_review_modal").modal({backdrop: "static"});
                var form = new RemoveOrderWidget(null, {});
                form.attachTo(self.$el.find('#cart_review_modal'));
            });
        },
        onBtnFoody: function (ev) {
            var name = this.id
            var imgurl = this.imgurl;
            var price= this.price.match(/^[-,0-9]+/)[0].replace(',', '');
            var self = this;
            ajax.jsonRpc("/autoOrder", 'call', {
                'name': name,
                'imgurl': imgurl,
                'price': price
            }).then(function (data) {
                self.$el.find("#place_modal").empty().append(data['lunch_order.cart_review']);
                self.$el.find("#cart_review_modal").modal({backdrop: "static"});
                var form = new RemoveOrderWidget(null, {});
                form.attachTo(self.$el.find('#cart_review_modal'));
            });
        }
    })
    $(function () {
        // TODO move this to another module, requiring dom_ready and rejecting
        // the returned deferred to get the proper message

        $('.nutrionist').each(function () {
            var id = $(this).find('a.orderbtn').attr('name');
            var form = new ConfirmOrderWidget(null, id, null);
            form.attachTo($(this));
        });
        $('.foodyproduct').each(function () {
            var name = $(this).find('a.btnfoodypro').attr('name');
            var imgurl = $(this).find('a.btnfoodypro').attr('src');
            var price = $(this).find('a.btnfoodypro').attr('price');
            var form = new ConfirmOrderWidget(null, name,imgurl,price);
            form.attachTo($(this));
        });
        // $('.life').each(function () {
        //     var id = $(this).find('a.foodybtn').attr('name');
        //     var form = new RestaurantsWidget(null, id);
        //     form.attachTo($(this));
        // });
    });
})



