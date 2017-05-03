// ccc
$('div.submit-create-claim-page').on('click', 'span.submit-create-claim-button', function(event){
	// event.preventDefault();
	// event.stopPropagation();

	order_id = $(this).data('order_id');
	// order_id = parseInt($("span[name='order_id']").val(),10);
	alert(order_id);
	openerp.jsonRpc("/m/myaccount/order/after_sale/claim_create/", "call", {});
	debugger
});

// 售后列表,局部刷新

$("div.mobile_after_sale_tag").on("click","div.om-choice",function(event){
    event.preventDefault();
    event.stopPropagation();
    var string_id = $(this).attr("id");
    // 确保数据源只有一处
    var categary_source = {
        "om-choice-1": "waitting_claim",
        "om-choice-2": "already_claimed",
    };
    var categary = categary_source[string_id];
    var $parent= $(this).closest('div.mobile_after_sale_tag');
    var $order_list_flag_input = $parent.find("input[name='tmp_orderlist_flag']");
    // 使用<input type='hidden' /> 临时存值
    $order_list_flag_input.val(categary);
    // var e = jQuery.Event("change");
    // 主动抛出 change事件
    $order_list_flag_input.trigger("change");

    var limit = 10;
    var offset = 0;
    openerp.jsonRpc("/m/myaccount/order/after_sale_main/ajax/"+categary, 'call', {'categary': categary,'limit':limit,'offset':offset})
        .then(function (data) {
            $("div.after_sale_foreach_tag").addClass("mopl-active"); 
            $("div.om-choice-status").html(data.categary_tab);
            $("div.after_sale_foreach_tag").html(data.orderlist);
        });
});

// 售后页面点击删除，进行数据隐藏
$('div.shopping-cart-page').on('click', 'a.after_sale_delete_line', function (event) {
    event.preventDefault();
    event.stopPropagation();
    if(confirm("确认不对该宝贝进行售后申请吗?"))
    {
        var item_id = parseInt($(this).data('item-id'),10);
        var order_id = parseInt($(this).data('order_id'),10);
        openerp.jsonRpc("/m/myaccount/order/after_sale/delete_line_json", 'call', {
            'order_id': order_id,
            'item_id': item_id})
            .then(function (data) {
                $(".sc-product-list").html(data.mobile_after_sale_product_line);
            });
    }
});

// edit jinchao's JS for my claims product list: 2017.03.31
$(function(){
    var $has_orderlist_product_obj = $('html body div.mobile_after_sale_tag div.mopl-active div.od-pd-detail');
    if ($has_orderlist_product_obj) {
        var $parent= $has_orderlist_product_obj.closest('div.mobile_after_sale_tag');
        var $order_list_flag_input = $parent.find("input[name='tmp_orderlist_flag']");
        var $foreach_order_list = $parent.find("div.after_sale_foreach_tag");

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

        if (categary == 0) {
            return false;
        }

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
            openerp.jsonRpc("/m/myaccount/order/after_sale_main/ajax/"+categary, 'call', {'categary': categary,'limit':limit,'offset':offset})
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