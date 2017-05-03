//  +begin:  by jinchao ====================description: in /m/myaacount/coupon , tab 切换
// 优惠券窗口, tab 切换
$("div.moblie-discount-coupon").on("click","div.od-choice",function(event){
    //获取点击id
    var id = $(this).attr("id");
    console.log('is clicked()! coupon tab , od-choice, id is ',id);
    $('.od-choice').removeClass("od-active");
    $(this).addClass("od-active");
    $('.od-coupon-list').removeClass("odol-active");
    $("."+id).addClass("odol-active"); 
});
//  +end: by jinchao 

//  +begin:  by jinchao ====================description: 订单列表,局部刷新
// categary_tab is 全部,待支付,待发货,待收货,待评价

$("div.mobile_orderlist_tag").on("click","div.om-choice",function(event){
    event.preventDefault();
    event.stopPropagation();
    var string_id = $(this).attr("id");
    console.log('string_id is',string_id);
    // 确保数据源只有一处
    var categary_source = {
        "om-choice-1": "all",
        "om-choice-2": "draft",
        "om-choice-3": "undelivered",
        "om-choice-4": "wait_delivery",
        "om-choice-5": "wait_comment"
    };
    var categary = categary_source[string_id];
    var $parent= $(this).closest('div.mobile_orderlist_tag');
    var $order_list_flag_input = $parent.find("input[name='tmp_orderlist_flag']");
    // 使用<input type='hidden' /> 临时存值
    $order_list_flag_input.val(categary);
    // var e = jQuery.Event("change");
    // 主动抛出 change事件
    $order_list_flag_input.trigger("change");

    var limit = 10;
    var offset = 0;
    openerp.jsonRpc("/m/myaccount/orderlist/ajax/"+categary, 'call', {'categary': categary,'limit':limit,'offset':offset})
        .then(function (data) {
            $("div.orderlist_foreach_tag").addClass("mopl-active"); 
            $("div.om-choice-status").html(data.categary_tab);
            $("div.orderlist_foreach_tag").html(data.orderlist);
        });
});
//  +end: by jinchao

    //  +begin:  by jinchao ====================description: 取消订单 btn
    $("div.moblie-order-management").on("click","a.public_btn_draft_cancel_tag",function(event){
        console.log('is click() public_btn_draft_cancel_tag');
        event.preventDefault();
        event.stopPropagation();

    if(confirm("确认要删除该订单吗?"))
    {
        openerp.jsonRpc("/m/myaccount/orderlist/action/draft_cancel", 'call', {'action': 'draft_cancel','order_id':$(this).data('order-id')})
            .then(function (data) {
                $("div.orderlist_foreach_tag").addClass("mopl-active");
                $("div.om-choice-status").html(data.categary_tab);
                $("div.orderlist_foreach_tag").html(data.orderlist);

                // $("span.om-tab-sub").html(data.order_list_count);
                // $("div.orderlist_foreach_tag").html(data.orderlist);
            });
    }
});

    //  +end: by jinchao

    //  +begin:  by jinchao ====================description: call weixin_pay window
    $("div.moblie-order-management").on("click","a.public_btn_goto_checkout_tag",function(event){
        console.log('is click() public_btn_goto_checkout_tag');
        event.preventDefault();
        event.stopPropagation();
        // 弹出支付方式窗口
        if($('.os-payment-list').hasClass('pm-list-open')){
            $('.os-payment-list').removeClass('pm-list-open').animate({bottom:-bodyheight},'slow');
            $(".modal-pop").css("display","none");
        }else{
            $('.os-payment-list').addClass('pm-list-open').animate({bottom:'0px'},'slow');
            $(".modal-pop").css("display","block");
        }

    }); //  +end: by jinchao

    console.log('is called! m_myaccount.js');
    // $(".personal-info").on("click","li.m_myaccount_address_edit",function(event){
    //     event.preventDefault();
    //     event.stopPropagation();
    //     if($('.os-adress-list').hasClass('ad-list-open')){
    //         $('.os-adress-list').removeClass('ad-list-open').animate({bottom:-bodyheight},'slow');
    //         $(".modal-pop").css("display","none");
    //     }else{ 
    //         $('.os-adress-list').addClass('ad-list-open').animate({bottom:'0px'},'slow');
    //         $(".modal-pop").css("display","block");
    //     }
    //     debugger;
    // });

    //  +begin:  by jinchao ====================description:  localhost/mobile_myaccount_distribution_ordersManager
    $(".distribution_ordersManager_tag").on("click","div.om-choice",function(event){
        event.preventDefault();
        event.stopPropagation();
        console.log('is click!  div#om-choice-2');
        var state = $(this).data('state');
        console.log('state is ',state);
        openerp.jsonRpc("/m/myaccount/distribution/ordersmanager_post", 'call', {'state': state})
            .then(function (data) {
                console.log('data is ',data.commission_lines);
                $(".distribution_ordersManager_list_tag").addClass("mopl-active"); 
                $(".distribution_ordersManager_list_tag").html(data.commission_lines);
            });

}); // +end: by jinchao

//  +begin:  by jinchao ====================description:  auto height , /m/myaccount/order/logistics_detail/<order_id>

// 物流详情页面的自动高度处理
$('div.show_order_logistics_page_tag ol.ui-ver-step li .log_context_tag').each(function(){
    var log_context_height = $(this).height();
    var $li = $(this).closest('li');
    $li.css('height',log_context_height+'px');
    var $step_line = $li.find('div.ui-ver-step-line');
    $li.css('height',log_context_height+'px');
    $step_line.css('height',(log_context_height+25)+'px');
    console.log("li is "+$li);
    console.log("step_line is "+$step_line);
    console.log("height is ",$(this).height());
});
//  +end: by jinchao 

//  +begin:  by jinchao ====================description: /m/myaccount/red_envelopes 红包页面
$("div.moblie-red-envelopes .rdh-choice").click(function(event){
    event.preventDefault();
    event.stopPropagation();
    //获取点击id
    var id = $(this).attr("id");
    $('.rdh-choice').removeClass("rdh-active");
    $(this).addClass("rdh-active");
    $('.rd-record-list').removeClass("rdh-active");
    $("."+id).addClass("rdh-active"); 
});
//  +end: by jinchao
