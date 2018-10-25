odoo.define('lunch_order.Restaurants', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var Dialog = require("web.Dialog");
    var Widget = require("web.Widget");
    var rpc = require("web.rpc");
    var _t = core._t;

    var RestaurantsWidget = Widget.extend({
        events: {
            'click .foodybtn': 'onBtnFoody',
        },
        init: function (parent, id) {
            this._super(parent);
            this.parent = parent;
            this.id = id;
        },
        onBtnFoody: function (ev) {
            var $this = $(this);
            var item_id = this.id;
            var oldurl = window.location.origin + "" + window.location.pathname+ item_id;
            window.location = oldurl;
        }
    })

    $(function () {
        // TODO move this to another module, requiring dom_ready and rejecting
        // the returned deferred to get the proper message

        $('.life').each(function () {
            var id = $(this).find('a.foodybtn').attr('name');
            var form = new RestaurantsWidget(null, id);
            form.attachTo($(this));
        });
    });
})



