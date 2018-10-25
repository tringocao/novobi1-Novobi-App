odoo.define('lunch_order.ImgTable', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var _t = core._t;


    var ImgTableWidget = Widget.extend({
        template: 'ImgTableView',
        events: {
            'click .btnUpdate': 'onClickUpdate'
        },
        init: function (parent, options) {
            var self = this;
            this._super.apply(this, arguments);
            this.parent = parent;
            this.items = options.context.items;
            this.sale_order_id = options.context.active_id;
        },
        onClickUpdate: function () {
            var self = this;
            var items_id = this.$el.find('input[name=selected]:checked').val();
            if (items_id == undefined) {
                this.do_warn(_t("Warning"), _t("Please select one of options"));
                return false;
            }
            var items = _.find(this.items, function (items) {
                return items['link'] == items_id
            })
             var data = {
                // chubb_plan_id: plan['id'],
                link: items['link'],
            }
            ajax.jsonpRpc('/web/dataset/call_kw', 'call', {
                model: 'lunch.product',
                method: 'update_selected_plan',
                args: [[this.sale_order_id], data],
                kwargs: {}
            }).then(function (result) {
                var index = 1;
                if (self.parent.inner_action.action_descr.view_id == undefined)
                    index = 0
                self.parent.select_action(self.parent.inner_action, index)
            });
        },

    })
    core.action_registry.add('lunch_order.img', ImgTableWidget);
})