$('.btn-block').click(function(){
    old_password = $('#old_password').val();
    new_password = $('#new_password').val();
    second_password = $('#second_password').val();

    if(old_password == '' || new_password == '' || second_password == ''){
        alert('不能留空！');
        return;
    } else if (old_password == new_password ){
        alert('旧密码不可重复使用！');
        return;
    }else if(new_password != second_password){
        alert('两次密码不同!');
        return;
    }

    $.post(
        '/auth/change_password',
        {
            'old_password':old_password,
            'new_password':new_password,
            'second_password':second_password
        },function(data){
            if(data['code'] == 200){
                location.href = '/auth/logout';
            }else if(data['code'] == 400){
                location.href = '/auth/change_password';
            }
        }
    )
})

