$(document).ready(function(){
    var checked_val = $("input[name='default_acquirer_id']").attr("value");

    // 动态给定选中状态，并处理相关数据 Liuzm 20170518
    $("input[value='" + checked_val + "']").attr("checked","checked");
    $(".payment-type input").click(function(){
        var value = $(this).attr("value");
        $("input[value='" + value + "']").attr("checked","checked");
        $("input[name='default_acquirer_id']").attr("value",value);
    });

    $("#compute_commission").click(function(){
        var partner_id = $("#get_partne_id").attr("value");
        openerp.jsonRpc("/payment/pay2user/compute_commission", 'call', {
            'partner_id':partner_id
        });
    });

    $(".pay_commission").click(function(){
        var invoice_id = $(this).attr("value");
        openerp.jsonRpc("/payment/pay2user/pay_commission", 'call', {
            'invoice_id':invoice_id
        }).then(function (data) {
            $(this).addClass("wip-ed");
            $(this).removeClass("pay_commission");
        });
    });
});