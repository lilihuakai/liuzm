
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
