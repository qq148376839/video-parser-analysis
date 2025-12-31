
<!DOCTYPE html>
<html>
<head>

<!--//不缓存代码-->
<meta HTTP-EQUIV="pragma" CONTENT="no-cache"> 
<meta HTTP-EQUIV="Cache-Control" CONTENT="no-cache, must-revalidate"> 
<meta HTTP-EQUIV="expires" CONTENT="0">
<!--//不缓存代码-->
<!--这里开始-->
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<meta name="viewport" content="width=device-width,user-scalable=no,initial-scale=1,maximum-scale=1,minimum-scale=1,viewport-fit=cover">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"><!-- IE内核 强制使用最新的引擎渲染网页 -->
<meta name="renderer" content="webkit">  <!-- 启用360浏览器的极速模式(webkit) -->
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"/>
<meta name="x5-fullscreen" content="true"/>
<meta name="x5-page-mode" content="app"/> <!-- X 全屏处理 -->
<meta name="full-screen" content="yes" />
<meta name="browsermode" content="application" />  <!-- UC 全屏应用模式 -->
<meta name="apple-mobile-web-app-capable" content="yes "/> <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" /> <!--  苹果全屏应用模式 --> 

<meta name="theme-color" content="#de698c">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
<meta name="format-detection" content="telephone=no">
<meta http-equiv="Cache-Control" content="no-transform">
<meta http-equiv="Content-Type" content="text/html;charset=utf-8">
<meta name="applicable-device" content="mobile">
<meta name="screen-orientation" content="portrait">
<meta name="x5-orientation" content="portrait">

<!--这里结束-->
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<meta charset="UTF-8">
<meta name="referrer" content="never">
  
  
<link rel="stylesheet" href="/playerapi/css/yzmplayer.css">
<style>
    .yzmplayer-setting-speeds:hover .title, .yzmplayer .yzmplayer-controller .yzmplayer-icons.yzmplayer-comment-box .yzm-yzmplayer-send-icon {
    	background-color: #33CC00 !important;
    }
    .showdan-setting .yzmplayer-toggle input+label, .yzmplayer-volume-bar-inner, .yzmplayer-thumb, .yzmplayer-played, .yzmplayer-comment-setting-box .yzmplayer-setting-danmaku .yzmplayer-danmaku-bar-wrap .yzmplayer-danmaku-bar .yzmplayer-danmaku-bar-inner, .yzmplayer-controller .yzmplayer-icons .yzmplayer-toggle input+label, .yzmplayer-controller .yzmplayer-icons.yzmplayer-comment-box .yzmplayer-comment-setting-box .yzmplayer-comment-setting-type input:checked+span, .yzmplayer-controller .yzmplayer-icons.yzmplayer-comment-box .yzmplayer-comment-setting-box .yzmplayer-comment-setting-font input:checked+span  {
        background: #33CC00 !important;
    }
    .yzmplayer-logo {
        width: 210px !important;
        height: 250px !important;
    }
</style>
<script src="/playerapi/js/jquery.min.js"></script>
<script src="/playerapi/js/7zl.js"></script>
<script src="/playerapi/js/7zlplayer.js"></script>
	<script type="text/javascript" src="/playerapi/js/hls.min.js"></script>
<script src="/playerapi/js/layer.js"></script>
</head>
<body>
<div id="player"></div>
<div id="ADplayer"></div>
<div id="ADtip"></div>
<script>
    

    var up = {
        "usernum": "965",
        "mylink": "",
        "diyid": [0, "游客", 1]
    }
    
    var config = {
        "api": "/dmku/",
        "av": "",
        "url": "O/zpjS4gC4ztyL9ve/+wx/3Lmpl7X/QAEOuqmTie93atrwDjwxRosEpoaXZw0TRD/AGtcvvIxMxgcxsQWcHumCqsvuIlf3lGXkqJgVWIsvPYgh8+Nsu4r36vZQ6fs/7edsA0WFSEDE16mwOTvC8ByCxFQJXZcJaeTf7igGItTKkNAp5yEF325qV9KNQuP/wR3si83JgFlTJ5d+hDqD6PjLpnQa9dj5jhhU3CRZaUxnIK9d1Gy+UxI0HhDsyLRnS+c6C7NFAu8aOZ48zeKlJH14o6IB9Io39UOiPh13dLuq9QmSqwzty7th+dt0Pz3O5w3nOvyQn+yieU0tPg+eNwujrN79nX+8bTPr5FdGfgqCyn0wMhRA==",
    	"id":"b664f44e3be2ad57fdb6",
    	"sid":"",
    	"pic":"",
    	"title":"",
    	"next":"",
    	"user": "",
    	"group": "",
    }
    config.contextmenu = [{text:"极速解析",link:"https://www.2s0.cn"}];
    
    YKQ.start();
    
    var _clearTimer = window.setInterval(function(){

        var _rightWenzi = "极速解析";
        var _rightLink  = "https://www.2s0.cn";
        var _menuItemDom= $(".yzmplayer-menu .yzmplayer-menu-item").eq(1);
        
        if(_menuItemDom.length > 0 && _menuItemDom.html().length > 0){
            $("#my-loading", parent.document).remove();
            window.clearInterval(_clearTimer);
            _menuItemDom.find("a").attr("href",_rightLink);
            _menuItemDom.find("a").html(_rightWenzi);
            
        }
        
    });
    
</script>
<script>
function adCheck(){
 var myDate = new Date();
 var aaa=myDate.getHours();
 if(parseInt(aaa)>=0 && parseInt(aaa)<=5 ){  //投放时间设置（默认是凌晨1点到早上5点，根据自己的需求自己修改）
   return true;
 }else{
   return false;
 }
}
 if(adCheck()){
document.writeln('<script type="text/javascript" charset="UTF-8" async src=""><\/script>');//此处广告联盟js是放你广告联盟获取的js链接
 }
 </script>  

</body></html>