$("div.mobile_orderlist_tag").on("click","div.om-choice",function(event){
    event.preventDefault();
    event.stopPropagation();
    var string_id = $(this).attr("id");
    console.log('string_id is',string_id);
    // 确保数据源只有一处
    var categary_source = {
        "om-choice-5": "waiting_comment"
    };
    var categary = categary_source[string_id];
    if (!categary) return false;
    var $parent= $(this).closest('div.mobile_orderlist_tag');
    var $order_list_flag_input = $parent.find("input[name='tmp_orderlist_flag']");
    // 使用<input type='hidden' /> 临时存值
    $order_list_flag_input.val(categary);
    // var e = jQuery.Event("change");
    // 主动抛出 change事件
    $order_list_flag_input.trigger("change");

    var limit = 10;
    var offset = 0;
    openerp.jsonRpc("/m/myaccount/order/sale_comment/ajax/"+categary, 'call', {
        'categary': categary,
        'ajax': 2,
        'limit':limit,
        'offset':offset})
        .then(function (data) {
            $("div.orderlist_foreach_tag").addClass("mopl-active"); 
            $("div.om-choice-status").html(data.categary_tab);
            $("div.orderlist_foreach_tag").html(data.orderlist);
        });
});
