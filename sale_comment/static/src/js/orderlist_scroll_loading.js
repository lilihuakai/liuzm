
// 列表滚动刷新 add by Liuzm:20170331
$(function(){
    var $has_orderlist_product_obj = $('html body div.mobile_sale_comment_tag div.mopl-active div.od-pd-detail');
    if ($has_orderlist_product_obj) {
        var $parent= $has_orderlist_product_obj.closest('div.mobile_sale_comment_tag');
        var $order_list_flag_input = $parent.find("input[name='tmp_orderlist_flag']");
        var $foreach_order_list = $parent.find("div.sale_comment_foreach_tag");

        var categary = $order_list_flag_input.val();
        var limit = 0;
        var offset = 0;

        openerp.jsonRpc("/m/myaccount/orderlist/get_default_limit_offset", 'call', {'sid':1})
            .then(function (data) {
                limit = data.limit;
                // limit = 50;
                offset = limit;
                console.log('data='+data.limit);
            });

        $order_list_flag_input.change(function(){
            console.log('is called  input is change!');
            // 如果flag 被改变, 则重新初始化
            offset = limit;
        });

        function append_orderlist_product() {
            var not_enough_data = $parent.find("input[name='not_enough_data']").val();
            if (parseInt(not_enough_data) == 1) {
                public_hidden_loader();
                var height_dict = public_get_scroll_height();
                var scrollTop = height_dict['scroll_top'];
                $('body').scrollTop(scrollTop-10);
                alert("没有数据了");
                return false;
            }

            categary = $order_list_flag_input.val();
            openerp.jsonRpc("/m/myaccount/order/sale_comment/ajax/"+categary, 'call', {
                'categary': categary,
                'ajax': 3,
                'limit':limit,
                'offset':offset})
                .then(function (data) {

                    console.log('in post() offset= ,limit= '+offset+'  '+limit);
                    $foreach_order_list.append(data.orderlist);
                    offset += limit;
                });

            return true;
        }
    }

    public_customize_scroll_load_func(append_orderlist_product);
});