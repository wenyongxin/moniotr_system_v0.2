function select_image(){
    $('input[id=lefile2]').click();
    $('.l_update_button').removeAttr("disabled");
}

function update_images(id){
    if ($('#lefile2').val() == ''){
        alert('请点击头像上传！')
    }else{
        $('#update_file').submit();
        $('.l_rose').html('上传中....');
        var timer;
        timer = setInterval(function(){
            $.get(
                '/auth/update_image',
                {'id':id},
                function(data){
                    if(data['image']){
                        $('.l_avatar').attr('src',data['image']);
                        $('.l_rose').html(data['role']);
                        clearInterval(timer);
                    }
                }
            )
        },6000);
    }
}