$(document).ready(function() {

    //选择服务类型
    $('.shipping-type').click(function() {
        $('.shipping-type').removeClass("sl-active");
        $(this).addClass("sl-active");
    });
	
    // 页面跳转动作JS代码，放在另外存放 add by Liuzm 20170510
	//点击下一步
	// $('.submit-next-button button').click(function() {
	// 	//获取选择问题的值
	// 	var radio_value  = $('.question-list input:checked').val();
	// 	//获取服务类型的值
	// 	var service_value  = $('.service-list .sl-active').html();
	// 	//获取问题描述的值
	// 	var textarea_value  = $('.question-describe textarea').val();
 //        alert("请选择问题:"+radio_value+"\n 服务类型:"+service_value+"\n 问题描述:"+textarea_value);
 //    });

});

//单选框样式
$.fn.rdo = function() {

    return $(this).each(function(k, v) {

        var $this = $(v);
        if ($this.is(':radio') && !$this.data('radio-replaced')) {

            // add some data to this checkbox so we can avoid re-replacing it.
            $this.data('radio-replaced', true);

            // create HTML for the new checkbox.
            var $l = $('<label for="' + $this.attr('id') + '" class="radio"></label>');
            var $p = $('<span class="pip"></span>');

            // insert the HTML in before the checkbox.
            $l.append($p).insertBefore($this);
            $this.addClass('replaced');

            // check if the radio is checked, apply styling. trigger focus.
            $this.on('change',
            function() {

                $('label.radio').each(function(k, v) {

                    var $v = $(v);
                    if ($('#' + $v.attr('for')).is(':checked')) {
                        $v.addClass('on');
                    } else {
                        $v.removeClass('on');
                    }

                });

                $this.trigger('focus');

            });

            $this.on('focus',
            function() {
                $l.addClass('focus')
            });
            $this.on('blur',
            function() {
                $l.removeClass('focus')
            });

            // check if the radio is checked on init.
            $('label.radio').each(function(k, v) {

                var $v = $(v);
                if ($('#' + $v.attr('for')).is(':checked')) {
                    $v.addClass('on');
                } else {
                    $v.removeClass('on');
                }

            });

        }

    });

};

$(':radio').rdo();