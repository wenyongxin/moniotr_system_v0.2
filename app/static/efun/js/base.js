//从大到小function
function BigToSmall(){
	$('.left').removeClass('l_big').addClass('l_small').slideDown();
	$('.l_log').css('background-image',"url(../static/efun/images/log-smll.jpg)").slideDown();
	var new_left = $(window).width() - $('.left').width();
	$('.right').css('width',new_left + 'px').fadeIn();
}

//从小到大function
function SmallToBig(){
	$('.left').removeClass('l_small').addClass('l_big').slideDown();
	$('.l_log').css('background-image',"url(../static/efun/images/log.jpg)").slideDown();
	var new_left = $(window).width() - $('.left').width();
	$('.right').css('width',new_left + 'px').fadeIn();
}

//点击r_switch控制左侧栏宽度
$('.r_switch').click(function(){
	list_switch();
});


//用于防止页面在小的情况下刷新。左侧导航条消失
if($(window).width() - $('.left').width() < 1000){
	BigToSmall();
	show_avator();
}else{
	SmallToBig();
	show_avator();
}


//控制头像与用户名显示的按钮
function show_avator(){
	if($(window).width() < 600){
		$('.r_btn').hide('show');
	}else{
		$('.r_btn').show('show');
	}
}




//获取屏幕的大小而触发 list_switch()事件
$(window).resize(function(){
	var right_width = $(window).width() - $('.left').width();
	$('.right').css('width',right_width + 'px');
	if($(window).width() < 1000){
		BigToSmall();
		show_avator();
	}else{
		SmallToBig();
		show_avator();
	}
})


//点击控制左侧菜单栏的列表
function list_switch(){
	var left_width = $('.left').width();
	if (left_width > 200){
		BigToSmall();
	}else if (left_width > 70){
		SmallToBig();
	}
					
}



//导航栏
$('.l_title').click(function(){
	if($(this).find('span').eq(1).hasClass('glyphicon-plus')){
		$(this).find('span').removeClass('glyphicon-plus').addClass('glyphicon-minus');
	}else{
		$(this).find('span').removeClass('glyphicon-minus').addClass('glyphicon-plus');
	}
	var id = $(this).index('.l_title');
	$('.l_ul').eq(id).toggle('show',function(){
		$('li').click(function(){
			var url = $(this).find('.l_href').attr('href');
			location.href = url;
            $(this).show();
		});
	});
});



//鼠标移动显示下列列表框
$('.r_btn').hover(function(){
		$('.b_list').show();
	},function(){
		$('.b_list').hide();
});



//弹窗中的x号关闭按钮
$('.t_button').click(function(){
	$('.alert_size').hide();
});

//消息弹窗自动关闭功能
$(document).ready(function(){
    if($(".alert-style").is(":visible")==true){
        setTimeout(function(){
            $('.alert-style').fadeOut(1000);
        }, 500)
    }
});




////通知滚动条效果
//通知滚动条效果
$(function(){
    //$('.dowebok').liMarquee();
    //导航栏选择状态及展示功能不关闭
    $('.l_ul').each(function(event){
        var Event = event;
        var This = $(this);
        This.find('li').each(function(){
            if ($(this).find('a').attr('href') == window.location.pathname){
                $(this).addClass('li_active');
                $(this).parent().show();
                $('.l_title').eq(Event).find('span').removeClass('glyphicon-plus').addClass('glyphicon-minus');
            }
        })
    })
});




