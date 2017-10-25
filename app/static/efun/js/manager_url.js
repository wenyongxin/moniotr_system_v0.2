//{# 控制每个版块收缩显示功能 #}
$('.panel-heading').click(function(){
    var id = $(this).attr('id');
    var panel = '#panel-body-' + id;
    var button = '#h_button-' + id;
    var This = $(button).find('span');
    if(This.hasClass('glyphicon-chevron-down')){
        This.removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-up');
        $(panel).fadeOut(500);
    }else{
        This.removeClass('glyphicon-chevron-up').addClass('glyphicon-chevron-down');
        $(panel).fadeIn(1000);
    }
})

//{# section下拉列表管理，修改信息 #}
$('.dropdown-toggle').click(function(){
    $('.show_list').toggle();
})

//{# 返回id的值  #}
function return_id(){
    $('.show_list').hide();
    var id = $('.list_sesctions').val();
    return id
}

function sesction_edit(){
    var id = return_id();
    show_edit(id, type='edit');
}

function sesction_clone(){
    var id = return_id();
    show_edit(id, type='clone');
}

function sesction_delete(){
    var id = return_id();
    delete_url(id);
}

//{#  克隆信息 #}
function show_clone(id){
    show_edit(id, type="clone");
}

//{# 修改按钮功能并通过ajax的get方式获取html信息 #}
function show_edit(id, type='edit'){
    $('.t_text').text('信息修改');
    $.get(
        "/auth/manager_edit",
        {id:id},
        function(data){
            $('.t_content').html(data);
            if (type == 'clone'){
                $('#sesction_id').val('clone');
            }
        }
    )
    $('.alert_size').show();
}


//{# 上一页 #}
function page_up(page){
    var page = parseInt(page) - 1;
    if (page >= 1){
        show_icon(page);
    }else{
        console.log('已结最前了')
    }
}

//{# 下一页 #}
function page_down(page){
    var page = parseInt(page) + 1;
    console.log(page)
    if (page > 1 && page <= 4 ){
        show_icon(page);
    }else{
        console.log('已结最后了')
    }
}

//{# ajax 图标获取的函数 #}
function show_icon(page){
    $.get(
        "/auth/manager_icon",
        {page:page},
        function(data){
            $('.manager_icon').show();
            $('.manager_icon').html(data);
        }
    )
}

//{# 改变图标样式按钮 #}
function change_icon(icon_name){
    var new_class = "glyphicon " + icon_name;
    $('.icon_button').find('span').removeClass().addClass(new_class);
    $('.icon_button').find('input').val(icon_name);
    close_button();
}

//{# 关闭图标展示框 #}
function close_button(){
    $('.manager_icon').hide();
}

//{# 天窗提醒产出错误 #}
function delete_url(id){
    if(window.confirm("确认删除吗?")){
        location.href = '/auth/manager_delete?id=' + id;
    }
}