//{# 通过ajax方式重其它网页上获取数据放在本地弹窗中  #}
function permission_edit(id, type='edit'){
    $.ajax({
        'type':"GET",
        'url':"/auth/tree",
        'data':{'id':id},
        'async':true,
        'success':function(data){
            $('.t_content').html(data);
            if(type=='clone'){
                $('.t_text').text('权限复制');
                $('#action').val('clone');
            }else{
                $('.t_text').text('权限修改');
            }
            if(id==1){
                $('.dtree').addClass('disable_alert');
                $('.c_left').click(function(){
                    alert('超级管理员不可修改权限')
                });
            }
        }
    })
    $('.alert_size').show();
}

//{# 重构关闭弹窗的按钮。并增加清空消息框内容   #}
$('.t_button').click(function(){
    $('.alert_size').hide();
    $('.t_content').html('');
});

//{# 更新修改信息 #}
function update_data(permissionid){
    var chckboxinfo = {};
    var checkboxall = $(':checkbox');
    for(i=0; i<checkboxall.length; i++) {
        var check_val = parseInt(checkboxall.eq(i).val());
        var check_status = checkboxall.get(i).checked;
        if (check_status){
            chckboxinfo[check_val] = 'true'
        }else{
            chckboxinfo[check_val] = 'false'
        }
    }
    var id = $('#action').val();
    var newname = $('#name').val();
    var newdes = $('#desc').val();

    $.post(
        '/auth/permission_update',
        {
            'id':id,
            'newname':newname,
            'newdesc':newdes,
            'chckboxinfo':JSON.stringify(chckboxinfo)
        },
        function(data){
            if(data['code'] == 200){
                location.href = '/auth/manager_permission'
            }
        }
    )
}

//{# 查看当前权限下包含哪些用户 #}
function show_users(id){
    $.post(
        '/auth/permission_users',
        {'id':id},
        function(data){
            $('.t_text').text('关联用户信息');
            $('.t_content').html(data['users']);
            $('.alert_size').show();
        }
    )
}

//{# 删除权限 #}
function permission_delete(id) {
    if(id != 1){
        if (window.confirm("确定要删除吗?")) {
            $.get(
                '/auth/permission_users',
                {'id': id},
                function (data) {
                    if(data['code'] == 200){
                        location.href = '/auth/manager_permission';
                    }else{
                        alert(data['message']);
                    }
                }
            )
        }
    }else{
        alert('管理员禁止删除！')
    }
}