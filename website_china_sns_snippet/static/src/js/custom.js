// function share_weibo(){
var my_desc = document.getElementsByName('description')[0].getAttribute('content');
var my_title=document.title;
var my_current_url = window.location.href;
var weibo_share_url = 'http://service.weibo.com/share/share.php?title='+my_desc+'&url='+my_current_url;

// 因为QZONE的API 不能含有localhost , 遂转换成127.0.0.1
my_current_url = my_current_url.replace("http://localhost","http://127.0.0.1");
my_current_url = my_current_url.replace("https://localhost","https://127.0.0.1");
var qzone_share_url = 'http://sns.qzone.qq.com/cgi-bin/qzshare/cgi_qzshare_onekey?url='+my_current_url+'&title='+my_title+'&desc='+my_desc;
// var qzone_share_url = 'http://sns.qzone.qq.com/cgi-bin/qzshare/cgi_qzshare_onekey?url='+my_current_url+'&title='+my_title+'&desc='+my_desc;
// window.open(my_share_url,'','menubar=no,toolbar=no,resizable=yes,scrollbars=yes,height=480,width=640');
// };
document.getElementById('share_weibo_tag').setAttribute("href",weibo_share_url);
document.getElementById('share_qzone_tag').setAttribute("href",qzone_share_url);