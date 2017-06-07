$(document).ready(function(){
    var state_val = $("input[name='tmp_state_flag']").attr("value");

    // 暂时只处理新建时的状态，以后再添加其他状态的处理 add by liuzm 20170607
    if (state_val == "新建" || state_val == "New"){
        $("#operation1").addClass("sd_pc_done")
        $("#operation_line1").addClass("sd_pc_ongoing")
    }
});