// 订单搜索功能 add by liuzm 20170106
$(".public_mobile_order_top_menu").on("click","button.mobile_order_search_button",function(event){
    var search_text = $(".mobile_order_search_input").val();

    openerp.jsonRpc("/m/myaccount/orderlist_search", 'call', {
    // openerp.jsonRpc("/m/myaccount/distribution/productPromotion_post", 'call', {
        'search_text': search_text})
        .then(function (data) {
            console.log('data is ',data.orders);
            $(".mo-order-pd-list").html(data.orders);
        });
});