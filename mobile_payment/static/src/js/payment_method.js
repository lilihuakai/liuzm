$(document).ready(function(){
    var checked_val = $("input[name='default_acquirer_id']").attr("value");

    // 动态给定选中状态，并处理相关数据 Liuzm 20170518
    $("input[value='" + checked_val + "']").attr("checked","checked");
    $(".payment-type input").click(function(){
        var value = $(this).attr("value");
        $("input[value='" + value + "']").attr("checked","checked");
        $("input[name='default_acquirer_id']").attr("value",value);
    });
});