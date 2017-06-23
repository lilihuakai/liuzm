$(document).ready(function(){
	
	$(".mos-choice").click(function(){
       //获取点击id
       var id = $(this).attr("id");
	   $('.mos-choice').removeClass("mos-active");
	   $(this).addClass("mos-active");
	   
	   $('.moe-order-list').removeClass("mol-active");
	   $("."+id).addClass("mol-active"); 
    });
	
	// $(".pes-choice").click(function(){
 //       //获取点击id
 //       var id = $(this).attr("id");
	//    $('.pes-choice').removeClass("pes-active");
	//    $(this).addClass("pes-active");
	   
	//    $('.pie-evaluation-list').removeClass("pel-active");
	//    $("."+id).addClass("pel-active"); 
 //    });
    
	//评分星星
	$.fn.raty.defaults.path = 'images';
    $('#ms-raty').raty();	
	$('.pie-star').raty({ readOnly: true, score: 3 });
	
	
	
	
	
	
});