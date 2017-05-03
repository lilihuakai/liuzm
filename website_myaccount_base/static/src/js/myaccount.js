(function () {
    'use strict';

    var _t = openerp._t;

    openerp.website.ready().done(function() {
        $('#myaccount-profile').on('submit', function(event){
            debugger;
            event.preventDefault();
            var data = {name: $('#name').val() };

            if($('#email-current').val() != $('#email').val()){
                var filter = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
                if($('#email').val().length == 0){
                    alert('Please fill email field');
                    $('#email').focus();
                    return;
                } else if($('#email-confirm').val() != $('#email').val()){
                    alert('The email address don\'t match!');
                    $('#email-confirm').focus();
                    return;
                } else if(!filter.test($('#email').val())){
                    alert('You have entered an invalid email address!');
                    $('#email').focus();
                    return;
                } else {
                    data['email'] = $('#email').val();
                }
            }

            if($('#password').val().length != 0){
                if($('#password').val() != $('#password-confirm').val()){
                    alert('Password don\'t match!');
                    $('#password-confirm').val('');
                    $('#password-confirm').focus();
                    return;
                } else {
                    data['password'] = $('#password').val();
                }
            }

            data['mobile'] = $('#mobile').val();
            data['birthday'] = $('#birthday').val();

            openerp.jsonRpc('/myaccount/profile/update', 'call', {
                data: data
            }).then(function(result) {
                $('#profile_error').html(result['error'])
            });
        });

        $('#myaccount-default-address').on('submit', function(event){
            event.preventDefault();
            var data = {street: $('#street').val() }
            data['street2'] = $('#street2').val();
            data['city'] = $('#city').val();
            data['zip'] = $('#zip').val();

            openerp.jsonRpc('/myaccount/default_address/update', 'call', {
                data: data
            }).then(function(result) {
                console.log(result);
                if(result['result'] == true){
                    location = '/myaccount';
                }
            });
        });

        // $.datepicker.regional['zh-CN'] = {  
        //     closeText: '关闭',  
        //     prevText: '<上月',  
        //     nextText: '下月>',  
        //     currentText: '今天',  
        //     monthNames: ['一月','二月','三月','四月','五月','六月',  
        //     '七月','八月','九月','十月','十一月','十二月'],  
        //     monthNamesShort: ['一月','二月','三月','四月','五月','六月',  
        //     '七月','八月','九月','十月','十一月','十二月'],  
        //     dayNames: ['星期日','星期一','星期二','星期三','星期四','星期五','星期六'],  
        //     dayNamesShort: ['周日','周一','周二','周三','周四','周五','周六'],  
        //     dayNamesMin: ['日','一','二','三','四','五','六'],  
        //     weekHeader: '周',  
        //     dateFormat: 'yy-mm-dd',  
        //     firstDay: 1,  
        //     isRTL: false,  
        //     showMonthAfterYear: true,  
        //     yearSuffix: '年'};  
        // $.datepicker.setDefaults($.datepicker.regional['zh-CN']);  

        // $.datepicker.setDefaults({
        //     clearText: _t('Clear'),
        //     clearStatus: _t('Erase the current date'),
        //     closeText: _t('Done'),
        //     closeStatus: _t('Close without change'),
        //     prevText: _t('<Prev'),
        //     prevStatus: _t('Show the previous month'),
        //     nextText: _t('Next>'),
        //     nextStatus: _t('Show the next month'),
        //     currentText: _t('Today'),
        //     currentStatus: _t('Show the current month'),
        //     monthNames: Date.CultureInfo.monthNames,
        //     monthNamesShort: Date.CultureInfo.abbreviatedMonthNames,
        //     monthStatus: _t('Show a different month'),
        //     yearStatus: _t('Show a different year'),
        //     weekHeader: _t('Wk'),
        //     weekStatus: _t('Week of the year'),
        //     dayNames: Date.CultureInfo.dayNames,
        //     dayNamesShort: Date.CultureInfo.abbreviatedDayNames,
        //     dayNamesMin: Date.CultureInfo.shortestDayNames,
        //     dayStatus: _t('Set DD as first week day'),
        //     dateStatus: _t('Select D, M d'),
        //     dateFormat: 'yy-mm-dd',
        //     firstDay: Date.CultureInfo.firstDayOfWeek,
        //     initStatus: _t('Select a date'),
        //     isRTL: false
        // });


        // $( "#birthday" ).datepicker({
        //   changeMonth: true,
        //   changeYear: true,
        //   showButtonPanel: true,
        //   yearRange: '-100:+0'
        // });
    });

})();


$(document).ready(function(){
});

var intDiff = parseInt(3600);//倒计时总秒数量
function timer(intDiff){
    window.setInterval(function(){
    var day=0,
        hour=0,
        minute=0,
        second=0;//时间默认值
    if(intDiff > 0){
        day = Math.floor(intDiff / (60 * 60 * 24));
        hour = Math.floor(intDiff / (60 * 60)) - (day * 24);
        minute = Math.floor(intDiff / 60) - (day * 24 * 60) - (hour * 60);
        second = Math.floor(intDiff) - (day * 24 * 60 * 60) - (hour * 60 * 60) - (minute * 60);
    }
    if (minute <= 9) minute = '0' + minute;
    if (second <= 9) second = '0' + second;
    $('#time_show').html('<s id="h"></s>'+hour+'时'+minute+'分'+second+'秒');
    intDiff--;
    }, 1000);
}
$(function(){
    timer(intDiff);
});
// $(function(){
// 	init_city_select($("#sel1"));
// });


