//自动与手动的选择器按钮
$('#operation_mode').bootstrapSwitch();
	$('#operation_mode').on('switchChange.bootstrapSwitch', function(event, state) {
		$('#mode').val(state);
		if(state){
			$('.f-ssh-div').hide();
			$('.col-md-3').removeClass('col-md-3').addClass('col-md-6');
			$("#install_system option[value='w']").hide();
		}else{
			$('.f-ssh-div').show();
			$('.col-md-6').removeClass('col-md-6').addClass('col-md-3');
			$("#install_system option[value='w']").show();
		}
});


//按照布尔值方式。返回1为正常。0为异常
//判断指定的id当前状态是否为隐藏，如果隐藏返回true，如果不隐藏，有值返回true，无值返回false
function input_status(input){
	var s = $(input).css('display');
	if (s == 'none'){
		return 1;
	}else{
		var find_str = $(input).val();
		if (find_str){
			return 1;
		}else{
			return 0;
		}
	}
}


//from表单提交时做验证，验证port与pwd的输入框状态是否为1，如果为1则正常提交，否则就return提醒
function from_check(){
	if (input_status('#login_port2') == 1 && input_status('#login_pwd2') == 1){
		console.log(status_windows)
	}else{
		alert('ssh端口与密码不能为空请检查!')
	}
}


//通过正则匹配IP是否合法
var ips = document.getElementById('login_ip');
ips.onkeyup = function(){
	var reg = /^((\d{1,3}\.)){3}\d{1,3}(,| ((\d{1,3}\.)){3}\d{1,3})*$/g;
	if(reg.test(this.value)){
		$(this).toggleClass('true')
		$('#install_buton').attr("disabled","disabled");
	}else{
		$(this).toggleClass('false')
		$('#install_buton').removeAttr("disabled");
	}
}


//安装界面点击加号按钮，将下拉列表变成input标签
function change_input(button, input, select){
	$(button).click(function(){
		var status = $(input).css('display');
		if (status == 'none'){
			$(input).show();
			$(select).hide();
		}else{
			$(select).show();
			$(input).hide();
		}
	});
}

change_input('.show-ssh', '#login_port2', '#login_port');
change_input('.show-pwd', '#login_pwd2', '#login_pwd');


















































