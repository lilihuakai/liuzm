$(document).ready(function(){
    $(".moblie-ws-faq li").click(function(){
        //»ñÈ¡µã»÷id
        var id = $(this).attr("id");
        //关闭所有二级Span
        $(".show-answer").css("display","none");
        //打开点击的Span
        $("#"+id+" .show-answer").css("display","block");
    });
    
    // delete by Liuzm 20170517
    // $(".payment-type input").click(function(){
    //     var value = $(this).attr("value");
    //     if(value =="alipay"){
    //         $(".wechat-payment").css("display","none");
    //         $(".alipay-payment").css("display","block");
    //     }else{
    //         $(".alipay-payment").css("display","none");
    //         $(".wechat-payment").css("display","block");
    //     }
    // });
    
    
    //2016-11-28

    $(".moblie-order-management").on("click","div.om-choice",function(event){
        console.log('om-choice is click! ');
        //获取点击id
        var id = $(this).attr("id");
        $('.om-choice').removeClass("om-active");
        $(this).addClass("om-active");
        $('.mo-order-pd-list').removeClass("mopl-active");
        $("."+id).addClass("mopl-active"); 
    });
});