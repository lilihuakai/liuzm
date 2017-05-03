//  +begin:  by jinchao ====================description: 只有当某页面含有某className, 才使用滚动刷新

// include in xml template_id ="website_myaccount_base.mobile_myaccount_distribution_productPromotion"
$(function(){
    var $has_orderlist_product_obj = $('div.pm-product-list table');
    if ($has_orderlist_product_obj) {
        var $parent= $has_orderlist_product_obj.closest('div.product-management-page');
        var $foreach_order_list = $parent.find("div.pm-product-list");
        var $order_list_flag_input = $parent.find("input[name='tmp_promotion_orderlist_flag']");

        var limit = 10;
        var offset = limit;

        $order_list_flag_input.change(function(){
            console.log('is called  input is change!');
            // 如果flag 被改变, 则重新初始化
            offset = limit;
            alert(document.documentElement.clientWidth);
            alert(document.documentElement.clientHeight);
        });
        function append_orderlist_product() {
            var not_enough_data = $parent.find("input[name='promotion_not_enough_data']").val();
            if (parseInt(not_enough_data) == 1) {
                public_hidden_loader();
                var height_dict = public_get_scroll_height();
                var scrollTop = height_dict['scroll_top'];
                $('body').scrollTop(scrollTop-10);
                alert("没有数据了");
                return false;
            }

            key = $order_list_flag_input.val();
            openerp.jsonRpc("/m/myaccount/distribution/productPromotion_post", 'call', {'sort_regexp':key ,'limit':limit,'offset':offset})
                .then(function (data) {
                    console.log('in post() offset= ,limit= ,key= '+offset+'  '+limit+'  '+key);
                    console.log("in post() data is ");
                    $foreach_order_list.append(data.promotion_lines);
                    offset += limit;
                });

            return true;
        }
    }

    public_customize_scroll_load_func(append_orderlist_product);
});
//  +end: by jinchao
