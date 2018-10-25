odoo.define('lunch_order.SaveConfirm', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var Dialog = require("web.Dialog");
    var Widget = require("web.Widget");
    var rpc = require("web.rpc");
    var _t = core._t;

    var SaveConfirm = Widget.extend({
        events: {
            'click .btnConfirmm': 'onBtnConfirm',
        },
        onBtnConfirm: function (ev) {
            var item_id = $(ev.currentTarget).data('id');

            ajax.jsonRpc("/confirmorder", 'call', {
                'item_id': item_id ,

            }).then(function (data) {
                var oldurl = window.location.origin + "" + window.location.pathname.replace("/confirm","");
                window.location = oldurl;
            });


            ev.stopPropagation();
        },


    })

    $(function () {
        // TODO move this to another module, requiring dom_ready and rejecting
        // the returned deferred to get the proper message
        var form = new SaveConfirm(null);
        form.attachTo($('.booking-wrapper'));
    });


})



