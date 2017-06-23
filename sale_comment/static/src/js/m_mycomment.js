$(document).ready(function(){
    $(".mwe-submit-button a").click(function(){
        // line_id = document.getElementById("line_id_flag").value;
        // ratings = document.getElementsByName("rating");
        // for (i = 0; i < ratings.length; i++)
        //     for (j = 0; j < ratings[i].length; j++)alert(ratings);
        //         alert("½ÚµãÀàÐÍ:"+ratings[i][j].nodeName+ratings[i][j].nodeType+ratings[i][j].nodeValue+"<br>");
        var line_id = $("#line_id_flag").val();
        var rating = $("#count-existing").val();
        var description  = $('#mwe-comments').val();
        if(document.getElementById("checkbox_mwe_a1").checked == true){
            var is_anonymous = true;
        }else{
            var is_anonymous = false;
        }
        alert("line_id is " + line_id + "\n; rating is " + rating + "\n is_anonymous is " + is_anonymous + "\n" + description);

        openerp.jsonRpc("/m/myaccount/order_line/sale_comment/create_comment/", 'call', {
            'line_id': line_id,
            'rating': rating,
            'description': description,
            'website_published': false,
            'is_anonymous': is_anonymous
        }) .then(function(res) {
            location.href = "/m/myaccount/order/sale_comment/waiting_comment";
        });
    });
});

// 产品评论列表,局部刷新

$("div.mobile_product_comment_tag").on("click","div.pes-choice",function(event){
    event.preventDefault();
    event.stopPropagation();
    var string_id = $(this).attr("id");
    // 确保数据源只有一处
    var categary_source = {
        "pes-choice-1": "all_comment",
        "pes-choice-2": "good_comment",
        "pes-choice-3": "no_bed_comment",
        "pes-choice-4": "bed_comment",
    };
    var categary = categary_source[string_id];
    var $parent= $(this).closest('div.mobile_product_comment_tag');
    var $order_list_flag_input = $parent.find("input[name='tmp_orderlist_flag']");
    // 使用<input type='hidden' /> 临时存值
    $order_list_flag_input.val(categary);
    // var e = jQuery.Event("change");
    // 主动抛出 change事件
    $order_list_flag_input.trigger("change");
    var product_tmp_id = document.getElementsByName("tmp_product_tmp_id_flag")[0].getAttribute("value");

    openerp.jsonRpc("/m/myaccount/product/"+product_tmp_id+"/sale_comment/ajax/"+categary, 'call', {})
        .then(function (data) {
            $("div.product_comment_foreach_tag").addClass("pes-active"); 
            $("div.pie-evaluation-status").html(data.categary_tab);
            $("div.product_comment_foreach_tag").html(data.commentlist);
            $("div.public_foreach_pager").html(data.pager);
        });
});