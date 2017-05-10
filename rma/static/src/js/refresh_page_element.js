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
