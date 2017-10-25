//{#  登录框显示事件   #}
$(function(){
    $('.login_div').fadeIn(2000);
});

function error_message(mes){
    //{#  验证码验证信息返回  #}
    //{# 如果输入密码错误出现跳动效果 #}
    $('.error_message').text(mes);
    var panel = $(".login_div");
    for(var i=0; 1>=i; i++){
        panel.animate({top: '45%'}, 100)
        panel.animate({top: '50%'}, 100)
    }
    return false;
};


function send_data(){
    //{# 获取当前页面是否需要跳转#}
    var local_url = window.location.search;
    var email = $('#email').val();
    var password = $('#password').val();
    var captcha = $('#captcha').val();

    if (email == ''){
        var mes = "用户名不能为空"
    }else if(password == ''){
        var mes = "密码不能为空"
    }else if(captcha == ''){
        var mes = "验证码不能为空"
    }
    error_message(mes);


    var csrftoken = $('meta[name=csrf-token]').attr('content')
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        }
    })

    $.ajax({
        url:"/auth/login",
        type:"POST",
        dataType:'json',
        data:{
            'email': email,
            'password':password,
            'captcha':captcha,
            'remember_me':$('#remember_me').is(':checked'),
            'new_href':local_url
        },
        success: function(msg){
            if(msg['code'] == 200){
                //{# 页面跳转 #}
                window.location = msg['href'];
            }else if(msg['code'] == 500 || msg['code'] == 400){
                //{#  验证码验证信息返回  #}
                //{# 如果输入密码错误出现跳动效果 #}
                error_message(msg['des'])
                $('.captcha-img').click();
            }else if(msg['code'] == 600){
                alert(msg['des'])
                location.href = msg['href'];
                $('.captcha-img').click();
            }
        }
    })
};


//{# 登录提交事件 #}
$(function() {
    $('.btn').click(function () {
        send_data()
    })
});

//{# 回车键盘出发鼠标点击事件 #}
$(function() {
    $('html').bind('keydown', function (e) {
        if (e.keyCode == 13) {
            $('.btn').click();
        }
    })
});


//{#  验证码点击刷新事件 #}
$(function(){
    $('.captcha-img').click(function(){
        var old_src = $(this).attr('src');
        var src = old_src + '?update=' + Math.random();
        $(this).attr('src', src);
    })
});