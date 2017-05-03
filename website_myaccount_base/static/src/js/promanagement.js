// $(document).ready(function(){

    $("div.product-management-page").on("click","div.po-choice",function(event){
        // event.preventDefault();
        // event.stopPropagation();
        var id = $(this).attr("id");
        var sort_regexp= $(this).data('sort-regexp');
        var $parent= $(this).closest('div.product-management-page');
        
        console.log('in class sort_regexp is',sort_regexp);
        $('.po-choice').removeClass("po-active");
        $(this).addClass("po-active");

        if($("#"+id+" b").hasClass('po-down')){
            $("#"+id+" b").removeClass("po-down");
            $("#"+id+" b").addClass("po-up");
        }else{
            $("#"+id+" b").removeClass("po-up");
            $("#"+id+" b").addClass("po-down");
            sort_regexp=sort_regexp + ' desc';
        }
        var $order_list_flag_input = $parent.find("input[name='tmp_promotion_orderlist_flag']");
        // 使用<input type='hidden' /> 临时存值
        $order_list_flag_input.val(sort_regexp);
        // var e = jQuery.Event("change");
        // 主动抛出 change事件
        $order_list_flag_input.trigger("change");


        openerp.jsonRpc("/m/myaccount/distribution/productPromotion_post", 'call', {
            'sort_regexp': sort_regexp
        })
            .then(function (data) {
                $(".pm-product-list").html(data.promotion_lines);
            });

    });
// });