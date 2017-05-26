$(document).ready(function() {
    //点击设置售后订单的收货地址
    $(".consignee-claim_list_tag").on("click","div.consignee-item",function(event){
        event.preventDefault();
        event.stopPropagation();
        var shipto_id = $(this).data('shipto-id');
        var order_id = $(this).data('order_id');
        openerp.jsonRpc("/m/shop/cart/update_claim_order_shipto", 'call', {
            'shipto_id': shipto_id,
            'order_id': order_id})
            .then(function (data) {
                $('.os-cancel-button').click();
                $(".address-change").html(data.using_shipto);
            });
    });
});