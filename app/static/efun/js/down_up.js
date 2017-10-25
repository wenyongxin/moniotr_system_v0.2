//监控添加框缩放按钮开关                
function show_connent(a, b, c){
	a.click(function(){
		if($(this).find('span').eq(1).hasClass('glyphicon-chevron-down')){
			hide_button($(this), b)
			if(c == 'install'){
				change_result_height()
			}
			}else{
				show_button($(this), b)
			if(c == 'install'){
				$('.install_message .m_content').css('height', '350px').fadeIn();
			}
		}
	});
}


//隐藏按钮
function hide_button(a, b){
	a.find('span').eq(1).removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-up')
	b.hide();
}

//显示按钮
function show_button(a, b){
	a.find('span').eq(1).removeClass('glyphicon-chevron-up').addClass('glyphicon-chevron-down');
	b.show();
}
