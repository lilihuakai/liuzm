$(document).ready(function(){
    $(".payment-type input").click(function(){
        var value = $(this).attr("value");
        if(value =="alipay"){
            $(".wechat-payment").css("display","none");
            $(".alipay-payment").css("display","block");
        }else{
            $(".alipay-payment").css("display","none");
            $(".wechat-payment").css("display","block");
        }
    });
});