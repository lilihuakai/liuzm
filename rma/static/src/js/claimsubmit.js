$(document).ready(function() {
    //点击下一步
    $('.submit-next-button button').click(function() {
        //获取选择问题的值
        var radio_value  = $('.question-list input:checked').val();
        //获取服务类型的值
        var deal_method  = $('.service-list .sl-active').html();
        //获取问题描述的值
        var description  = $('.question-describe textarea').val();
        var order_id = $('.submit-next-button').data('order_id');
        alert("请选择问题:"+radio_value+"\n 服务类型:"+deal_method+"\n 问题描述:"+description+"\n 问题描述:"+order_id);
        openerp.jsonRpc("/m/myaccount/order/after_sale/set_claim/", 'call', {
            'order_id': order_id,
            'deal_method': deal_method,
            'claim_origin': radio_value,
            'description': description
        }) .then(function(res) {
            location.href = "/m/myaccount/order/after_sale/checkout/" + order_id;
        });
    });

});