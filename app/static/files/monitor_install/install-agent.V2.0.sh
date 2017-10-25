#!/bin/sh
#用途：用于各linux系统下自动安装zabbix-agnet
#适用操作系统：Centos Ubuntu Freebsd Ecool SUSE
#日期：2016年04月20日
#编写人：温永鑫
#版本号：V2.0
#更新日期：2016-12-13



ZABBIX="/usr/local/zabbix/sbin/zabbix_agentd"
ZABBIX_DIR=`pwd`
system=$1
public=$2
token=$4
monitor_url=$5
sleep_time=$6
userid=$7
#url='http://218.32.219.148:8080'
url='http://218.32.219.172:8800'
proxy_info(){
	echo -e "\033[49;32;1m 中国香港		103.227.128.16 \033[0m"
	echo -e "\033[49;32;1m 腾 讯 云		119.29.137.171 \033[0m"
        echo -e "\033[49;32;1m 台湾远传		218.32.219.148 \033[0m"
        echo -e "\033[49;32;1m 台湾中华		203.69.109.117 \033[0m"
        echo -e "\033[49;32;1m 韩    国		58.229.180.29 \033[0m"
        echo -e "\033[49;32;1m 东 南 亚		175.41.130.249 \033[0m"
        echo -e "\033[49;32;1m 欧    洲		54.93.169.149 \033[0m"
        echo -e "\033[49;32;1m 美    洲		54.207.73.140 \033[0m"
        echo -e "\033[49;32;1m 悉    尼		54.206.96.244 \033[0m"
}

system_info(){
	echo "系统类型：Centos  c , Ubuntu  u , Debian d , Freebsd  f , Ecool  e , SUSE  s"
}

install_info(){
	echo
	echo -e "-------------------\033[49;31;1m Information \033[0m------------------------"
	echo "该脚本可通过批量安装脚本执行安装，按照其脚本命令要求即可"
        echo "该脚本可单独执行适合于以下几种情况："
        echo "1、被监控机只有内网IP没有公网IP地址。"
        echo "2、必须选择对应的proxy地址，否则无法继续安装。"
	echo "考虑到在使用中会忘记对应信息的情况。这里可以直接交互式处理"
	echo "如果\$1位置未填写，则会提醒输入对应的系统简写。"
	echo "如果\$2位置未填写，则会系统自动匹配IP地址，无需人工处理。"
	echo "但是这点得注意，适合能够通过ifconfig命令看到公网IP的，如果是无法看到的要加入公网IP地址"
	echo "如果\$3位置未填写，则会提醒各proxy的信息。这里需要输入ip地址"
	echo "-------------------------------------------------------"
	use="\033[49;32;1m $0 <系统简写> <本机公网IP> <proxy的IP地址> \033[0m"
	echo -e $use
	echo
}


#将执行结果post到监控系统前端显示
myfun(){
        interface_url="http://$monitor_url/monitor/message_interface"
	code=$4
	now=`date +'%T'`
	if [ -z $code ];then
		code="1"
	fi
        curl -l -H "Content-type: application/json" -X POST -d "{'host':'$1', 'plan':'$2', 'message':'$3', 'code':'$code', 'time':'$now', 'token':'$token', 'userid':$userid}" $interface_url 2> /dev/null 
	if [ $? -ne 0 ];then
		echo "$1  $3"
	fi
}


#检测SELinux状体如果
check_selinux(){
	#selinux检测
    setenforce 0  #临时关闭SELinux
    sed 's/SELINUX=enable/SELINUX=disabled/g' /etc/selinux/config  #通过修改配置文件关闭selinux 下次机器重启后即可生效
    [ $? -eq 0 ] && myfun $address '4' 'SELinux已经关闭'
    myfun $address '4' 'SELinux检测无异常'
}

#环境检测
check_path(){
	#dns检测
	ping www.qq.com -c 2 > /dev/null 2>&1
	if [ $? -ne 0 ];then
		myfun $address '1' 'DNS配置异常'
		echo 'nameserver 114.114.114.114' >> /etc/resolv.conf
		[ $? -eq 0 ] && myfun $address '2' 'DNS配置以修复'
	else
		myfun $address '2' 'DNS检查无异常'
	fi

    #判断当前系统是否为centos，如果是centos后redhat系统则进行关闭selinux状态
    if $1 == 'c':
         check_path
    fi

	#关闭zabix残留
	kill -15 `ps aux | grep snmp | grep -v "grep" | awk '{print $2}'` > /dev/null 2>&1
	if [ $? -ne 0 ];then
		myfun $address '5' '发现snmp的进程并被关闭'	
	else
		myfun $address '5' '未发现snmp进程'	
	fi
        #检查zabbix-agent进程
        kill -15 `ps aux | grep zabbix_agentd | head -1 | awk '{print $2}'` > /dev/null 2>&1
	if [ $? -ne 0 ];then
		myfun $address '6' '发现zabbix的进程并被关闭'	
	else
		myfun $address '6' '未发现zabbix进程'	
	fi


	myfun $address '10' '检查完毕开始安装监控'
}




select_ip(){
	ifconfig > /dev/null 2>&1
	if [ $? -ne 0 ];then
		yum -y install net-tools > /dev/null 2>&1 && echo "This system is centos 7"
	fi
        IPADD=`ifconfig | awk '/inet /{gsub(/addr:/,"");print $2}' | grep -v '127.0.0.1'`
        address=`echo -n $IPADD | awk '{print $1}'`
}

if [ "$1" == "-h" ];then
	install_info
	exit
elif [ -s $1 ];then
	system_info
	read -p "Please input your install the system: " system	
fi

if [ -z $2 ];then
	select_ip
else
	echo $2 | grep "^[0-9]\{1,3\}\.\([0-9]\{1,3\}\.\)\{2\}[0-9]\{1,3\}$" > /dev/null 2>&1
	if [ $? -eq 0 ];then
	        address=$2
		public=$address
	else
		select_ip
	fi
fi

if [ -z $3 ];then
	proxy_info
	read -p "Please input proxy ip address: " proxy_ip
else
	proxy_ip=$3

fi

if [ -z $public ];then
        public=$address
fi

echo "---------------------------------------------------"
echo $0 $system $address $proxy_ip
echo "---------------------------------------------------"
if [ !-z $sleep_time ];then
	leep $sleep_time
fi


KEY(){
	[ -d /usr/local/zabbix/scripts ] 
	if [ $? -ne 0 ] ; then 
		mkdir /usr/local/zabbix/scripts
	fi
	tar -xf $ZABBIX_DIR/port.tar -C /usr/local/zabbix/scripts/
	[ $? -eq 0 ] && mv /usr/local/zabbix/scripts/my.cnf /usr/local/zabbix/scripts/.my.cnf
	[ $? -eq 0 ] && chmod a+x /usr/local/zabbix/scripts/*.sh
	[ $? -eq 0 ] && tar -xf ../key.tar -C /usr/local/zabbix/etc/zabbix_agentd.conf.d/
}

#平台脚本监控更新范围 71-79%
INSTALL_PT(){
	wget $url/pt/key-pt.tar > /dev/null 2>&1 && myfun $address '71' "平台监控key下载完毕" 
	[ $? -eq 0 ] && wget $url/pt/log_scripts.tar.gz  > /dev/null 2>&1 && myfun $address '73' "日志监控脚本下载完毕" 
	[ $? -eq 0 ] && tar xf key-pt.tar -C /usr/local/zabbix/etc/zabbix_agentd.conf.d  > /dev/null 2>&1 && myfun $address '74' "平台监控key已更新" 
	[ $? -eq 0 ] && tar xf log_scripts.tar.gz -C /usr/local/zabbix/scripts  > /dev/null 2>&1 && myfun $address '75' "日志监控脚本以更新" 
	[ $? -eq 0 ] && chown zabbix. /usr/local/zabbix/scripts/* && myfun $address '76' "更新属组zabbix"
	[ $? -eq 0 ] && chmod +x /usr/local/zabbix/scripts/* && myfun $address '77' "赋予执行权限"
	[ $? -eq 0 ] && rm -rf $ZABBIX_DIR/key-pt.tar > /dev/null 2>&1 && myfun $address '78' "删除平台key临时文件" 
	[ $? -eq 0 ] && rm -rf $ZABBIX_DIR/log_scripts.tar.gz > /dev/null 2>&1 && myfun $address '79' "删除平台日志监控临时文件" 
}

#进度在61-80%
INSTALL_AGENT(){
	tar -xf ./zabbix-2.4.4.tar.gz > /dev/null 2>&1 && myfun $address '61' "zabbix-2.4.4.tar.gz解压完毕"
	[ $? -eq 0 ] && cd zabbix-2.4.4 
	[ $? -eq 0 ] && ./configure --prefix=/usr/local/zabbix --enable-agent  > /dev/null 2>&1 && myfun $address '63' "zabbix-2.4.4 编译开始" 
	[ $? -eq 0 ] && make > /dev/null 2>&1 && myfun $address '65' "zabbix-2.4.4 make"
	[ $? -eq 0 ] && make install > /dev/null 2>&1 && myfun $address '67' "zabbix-2.4.4 make install"
	[ $? -eq 0 ] && mv $ZABBIX_DIR/zabbix_agentd.conf /usr/local/zabbix/etc/zabbix_agentd.conf && myfun $address '68' "zabbix 配置文件更新完毕"
	[ $? -eq 0 ] && KEY && myfun $address '70' "zabbix key更新完毕"
	[ $? -eq 0 ] && if [ "$system" == "c" ];then
				INSTALL_PT
			fi
	[ $? -eq 0 ] && if [ "$system" == "f" ];then
  				sed -i "" "s/Hostname=8.8.8.8/`echo Hostname=$public`/g" /usr/local/zabbix/etc/zabbix_agentd.conf
				[ $? -eq 0 ] && sed -i i"" "s/8.8.4.4/$proxy_ip:10928/g" /usr/local/zabbix/etc/zabbix_agentd.conf
			else 
				sed -i "s/Hostname=8.8.8.8/`echo Hostname=$public`/g" /usr/local/zabbix/etc/zabbix_agentd.conf 
				[ $? -eq 0 ] && sed -i "s/8.8.4.4/$proxy_ip:10928/g" /usr/local/zabbix/etc/zabbix_agentd.conf
			fi
	i=0
	while [ $i != 4 ];do
        	/usr/local/zabbix/sbin/zabbix_agentd > /dev/null 2>&1
	        zabbix_init=`ps aux | grep zabbix_agentd | grep -v grep | wc -l`
		if [ $zabbix_init -ne 0 ];then
                	myfun $address '80' "zabbix 启动完成"
                	break
	        else
                	myfun $address '80' "zabbix 启动异常 尝试 $i 次" "0"
	        fi
	        i=$((i+1))
	done
}

#进度在23-30%
DOWN(){
	wget $url/client/key.tar > /dev/null 2>&1 && myfun $address '23' "key.tar下载完毕"
	[ $? -eq 0 ] && wget $url/client/net-snmp-5.7.2.tar.gz > /dev/null 2>&1 && myfun $address '25' "net-snmp-5.7.2.tar.gz下载完毕" 
	[ $? -eq 0 ] && wget $url/client/port.tar > /dev/null 2>&1 && myfun $address '27' "port.tar下载完毕" 
	[ $? -eq 0 ] && wget $url/client/zabbix-2.4.4.tar.gz > /dev/null 2>&1 && myfun $address '29' "zabbix-2.4.4.tar.gz下载完毕"
	[ $? -eq 0 ] && wget $url/client/zabbix_agentd.conf > /dev/null 2>&1 && myfun $address '30' "zabbix_agentd.conf下载完毕" 
}

#删除临时文件进度在91-99%
DELE(){
	rm -rf $ZABBIX_DIR/key.tar* && myfun $address '91' "key.tar文件删除完成" 
	[ $? -eq 0 ] && rm -rf $ZABBIX_DIR/port.tar* && myfun $address '93' "port.tar文件删除完成" 
	[ $? -eq 0 ] && rm -rf $ZABBIX_DIR/net-snmp-5.7.2* && myfun $address '95' "net-snmp文件删除完成" 
	[ $? -eq 0 ] && rm -rf $ZABBIX_DIR/zabbix-2.4.4* && myfun $address '99' "zabbix-2.4.4文件删除完成" 
	myfun $address '100' "监控安装完毕"
}

#snmp安装在31-40%
SNMP(){
	tar -xf net-snmp-5.7.2.tar.gz && myfun $address '32' "net-snmp解压完毕"
	[ $? -eq 0 ] && cd net-snmp-5.7.2
	[ $? -eq 0 ] && ./configure --prefix=/usr/local/snmpd  <<EOF > /dev/null 2>&1 

2



EOF
	[ $? -eq 0 ] && myfun $address '34' "net-snm准备开始编译" 
	[ $? -eq 0 ] && make > /dev/null 2>&1 
	myfun $address '37' "net-snm编译完成"
	[ $? -eq 0 ] && make install > /dev/null 2>&1 
	myfun $address '38' "net-snmp安装完毕"
	[ $? -eq 0 ] && mv ../snmpd.conf /usr/local/snmpd/
	[ $? -eq 0 ] && /usr/local/snmpd/sbin/snmpd -c /usr/local/snmpd/snmpd.conf 
	myfun $address '40' "snmp已经运行"
	[ $? -eq 0 ] && cd $ZABBIX_DIR
}

#开机启动进度81-90%
INIT(){
                U=`grep -E "zabbix|snmp" $RC | wc -l`
                if [ $U -ne 2 ] ; then 
                        echo $ZABBIX >> $RC && myfun $address '85' "zabbix配置开机启动完成"
			echo $SNMP2 >> $RC && myfun $address '90' "snmp配置开机启动完成"
                else
			myfun $address '90' "zabbix与SNMP已配置开机启动"	
                fi
}

#防火墙进度51-60%
iptables_cmd(){
	myfun $address '51' "开始配置防火墙"
	if [ ! -f "/tmp/iptable" ]; then
		if [ -f "/etc/sysconfig/iptables" ];then
			/etc/init.d/iptables status > /dev/null 2>&1
			if [ $? -eq 0 ];then
				wget -P $ZABBIX_DIR $url/client/iptables_comd.txt > /dev/null 2>&1
				while read iptable;do
					$iptable
				done < $ZABBIX_DIR/iptables_comd.txt
				/etc/init.d/iptables save
				rm -rf $ZABBIX_DIR/iptables_comd.txt*
				myfun $address '55' "iptables配置完成"
				touch /tmp/iptable > /dev/null 2>&1
			else
				wget -P $ZABBIX_DIR $url/client/iptables_conf.txt > /dev/null 2>&1
				while read iptable;do
					sed -i "/OUTPUT/a $iptable" /etc/sysconfig/iptables
				done < $ZABBIX_DIR/iptables_conf.txt
				rm -rf $ZABBIX_DIR/iptables_conf.txt*
				myfun $address '55' "iptables配置完成"
				touch /tmp/iptable > /dev/null 2>&1
			fi
		else
			myfun $address '57' "未找到/etc/sysconfig/iptables文件"
		fi
	else
		myfun $address '60' "防火墙规则已经更新"
	fi
}

#进度范围在41-50%
Centos6(){
	myfun $address '41' "当前系统 centos6"
        /etc/init.d/snmpd restart > /dev/null 2>&1 
	if [ $? -eq 0 ];then
		myfun $address '45' "snmp服务启动完成"
	else
		myfun $address '45' "snmp启动异常" "0"
	fi
        [ $? -eq 0 ] && chkconfig snmpd on && myfun $address '50' "snmpd已配置开机启动" 
}

#进度范围41-50%
Centos7(){
	myfun $address '41' "当前系统 centos7"
        /bin/systemctl restart snmpd > /dev/null 2>&1 && myfun $address '45' "snmp服务启动完成" 
        [ $? -eq 0 ] && /bin/systemctl enable snmpd > /dev/null 2>&1 && myfun $address '50' "snmpd已配置开机启动" 
	chmod +x /etc/rc.d/rc.local
}


#进度到10%
check_path $system
case "$system" in
#centos/redhat
	c )
		echo "==== $public install software ====" 
		yum -y install wget > /dev/null 2>&1 && myfun $address '12' "wget安装完毕"
		yum -y install gcc make > /dev/null 2>&1 && myfun $address '14' "gcc make安装完毕" 
		yum -y install file > /dev/null 2>&1 && myfun $address '16' "file安装完毕" 
		yum -y install perl-devel > /dev/null 2>&1 && myfun $address '17' "perl-devel安装完毕" 
		yum -y install openssh-clients > /dev/null 2>&1 && myfun $address '19' "openssh-clients安装完毕" 
		yum -y install sysstat > /dev/null 2>&1 && myfun $address '20' "sysstat安装完毕"
		useradd -M -s /sbin/nologin zabbix > /dev/null 2>&1
		if [ $? -eq 0 ];then
			myfun $address '21' "zabbix用户创建完毕"
		else
			myfun $address '21' "zabbix用户已存在"
		fi
		echo "=========== $public Download File ==========" 
		#下载文件在22-30%范围
		DOWN
		echo "=========== $public Install SNMP ============" 
		#snmp安装在31-40%
		yum -y install net-snmp > /dev/null 2>&1 && myfun $address '31' "net-snmp安装完毕" 
		[ $? -eq 0 ] && yum -y install net-snmp-utils > /dev/null 2>&1 && myfun $address '33' "net-snmp-utils安装完毕" 
		[ $? -eq 0 ] && wget $url/client/snmpd.conf.yum > /dev/null 2>&1 && myfun $address '35' "snmpd.conf.yum配置文件下载完毕" 
		[ $? -eq 0 ] && mv ./snmpd.conf.yum /etc/snmp/snmpd.conf && myfun $address '40' "snmpd.conf配置文件已更新" 
		#snmp启动配置在41-50%
		#防火墙配置在51-60%
		Verson=`cat /etc/redhat-release | awk -F 'release' '{print $NF}' | awk -F '.' '{print $1}'`	
		if [ $Verson -eq 7 ];then
			Centos7
		else
			Centos6
			iptables_cmd
		fi
		echo "=========== $public Install Agent ==========" 
		#安装zabbix进度61-80%
		INSTALL_AGENT
		RC=/etc/rc.d/rc.local 
		#配置开机启动进度 81%-90%
		INIT
		echo "======= $public Delete down file ==========" 
		#删除临时文件 91-99%
		DELE
	;;
#ubuntu
	u )
		echo "==== $public install software ====" 
		var=`cat /etc/issue | awk '{print $2}' | awk -F '.' '{print $1}'` && myfun $address '2' "检测ubuntu的版本 $var"
		if [ $var -eq 12 ];then
			rm -rf /var/lib/apt/lists/* && myfun $address '3' "清空apt临时文件完成"
		fi
		apt-get -y install curl > /dev/null 2>&1
		apt-get -y install wget > /dev/null 2>&1 && myfun $address '5' "wget安装完成"
		apt-get -y update > /dev/null 2>&1 && myfun $address '8' "apt-get库更新完成" 
		apt-get -y install gcc > /dev/null 2>&1 && myfun $address '13' "安装gcc完成" 
		apt-get -y install make > /dev/null 2>&1 && myfun $address '15' "安装make工具完成" 
		apt-get -y install libperl-dev > /dev/null 2>&1 && myfun $address '18' "安装libperl工具完成" 
		useradd -M -s /sbin/nologin zabbix > /dev/null 2>&1 
		if [ $? -eq 0 ] ;then
			myfun $address '20' "创建zabbix用户完成"
		else
			myfun $address '20' "zabbix用户已经存在"
		fi


		echo "=========== $public Download File ==========" 
		#下载文件在22-30%范围
		DOWN
		echo "=========== $public Install SNMP ============" 
		#snmp安装在31-40%
		apt-get -y install snmpd snmp > /dev/null 2>&1 && myfun $address '31' "安装snmp完成" 
		[ $? -eq 0 ] && wget $url/client/snmpd.conf > /dev/null 2>&1 && myfun $address '33' "下载snmpd.conf配置文件完成" 
		[ $? -eq 0 ] && mv ./snmpd.conf /etc/snmp/snmpd.conf && myfun $address '38' "替换snmpd.conf配置文件完成" 
		[ $? -eq 0 ] && /etc/init.d/snmpd restart > /dev/null 2>&1 && myfun $address '40' "snmpd服务重启完毕" 
		echo "=========== $public Install Agent ==========" 
		#安装zabbix进度61-80%
		INSTALL_AGENT
		RC=/etc/rc.local
		SNMP2="service snmpd start"
		sed -i "/exit 0/"d $RC
		INIT
		echo "exit 0" >> $RC
		echo -e "======= \033[49;32;1m $public \033[0m Delete down file =========="
                DELE
	;;
	d )
		echo "==== $public install software ====" 
		rm -rf /var/cache/apt/archives/lock && myfun $address '2' "清除apt缓存完成"
		rm -rf /var/lib/dpkg/lock 
		source="deb http://http.us.debian.org/debian/ stable main" && myfun $address '4' "更新debian下载源完成"
		sed -i "s/^/#/g" /etc/apt/sources.list && myfun $address '5' "修改debian原配置已完成1"
		sed -i "2 s#^#$source\n#" /etc/apt/sources.list && myfun $address '8' "修改debian原配置已完成2"
		apt-get -y install curl > /dev/null 2>&1
		apt-get -y update > /dev/null 2>&1 && myfun $address '10' "更新完成" 
		apt-get -y install gcc > /dev/null 2>&1 && myfun $address '13' "安装gcc完成" 
		apt-get -y install make > /dev/null 2>&1 && myfun $address '16' "安装make完成" 
		apt-get -y install libperl-dev <<EOF > /dev/null 2>&1
q
EOF
		myfun $address '18' "安装libperl完成"
		useradd -M -s /sbin/nologin zabbix
		if [ $? -eq 0 ];then
			myfun $address '20' "zabbix用户创建完毕"
		else
			myfun $address '20' "zabbix用户已存在"
		fi
		echo "=========== $public Download File ==========" 
		wget $url/client/snmpd.conf > /dev/null 2>&1 myfun $address '21' "下载snmpd.conf文件完成" 
		#下载文件在22-30%范围
		DOWN
		echo "=========== $public Install SNMP ============" 
		#snmp安装在31-40%
		SNMP
		echo "=========== $public Install Agent ==========" 
		#安装zabbix进度61-80%
		INSTALL_AGENT
		RC=/etc/rc.local
		SNMP2="service snmpd start"
		sed -i "/exit 0/"d $RC
		INIT
		echo "exit 0" >> $RC
		echo -e "======= \033[49;32;1m $public \033[0m Delete down file =========="
                DELE
	;;
#freebsd
	f )
		echo "==== $public install libiconv====" 
		pkg_add $url/client/pack_freebsd/libidn-1.27.tbz > /dev/null 2>&1 && myfun $address '3' "安装libidn完成"
                [ $? -eq 0 ] && pkg_add $url/client/pack_freebsd/gettext-0.18.3.tbz > /dev/null 2>&1 && myfun $address '6' "安装gettext完成"
                [ $? -eq 0 ] && pkg_add $url/client/pack_freebsd/libiconv.tbz > /dev/null 2>&1 && myfun $address '9' "安装libiconv完成"
                [ $? -eq 0 ] && pkg_add $url/client/pack_freebsd/wget.tbz > /dev/null 2>&1 && myfun $address '12' "安装wget完成"
		[ $? -eq 0 ] && pkg_add $url/client/pack_freebsd/perl-5.14.4.tbz > /dev/null 2>&1 && myfun $address '15' "安装perl完成" 
		[ $? -eq 0 ] && pkg_add $url/client/pack_freebsd/net-snmp.tbz > /dev/null 2>&1 && myfun $address '18' "安装net-snmp完成" 
		echo "================= $public Install End ======================" 
		pw user add zabbix -s /sbin/nologin
		if [ $? -eq 0 ];then
			myfun $address '20' "zabbix用户创建完成"
		else
			myfun $address '20' "zabbix用户已经存在"
		fi
		echo "=========== $public Download File ==========" 
		#下载文件在22-30%范围
                DOWN
		echo "=========== $public Install SNMP ============" 
		#snmp安装在31-40%
		wget $url/client/snmpd.conf > /dev/null 2>&1 && myfun $address '32' "snmpd.conf配置文件下载完成" 
		[ $? -eq 0 ] && mv ./snmpd.conf /usr/local/etc/snmpd.conf && myfun $address '35' "snmpd.conf配置文件已经更新" 
		[ $? -eq 0 ] && echo "snmpd_conffile="/usr/local/etc/snmpd.conf"" >> /etc/rc.conf 
		[ $? -eq 0 ] && echo "snmpd_enable="YES"" >> /etc/rc.conf
		myfun $address '38' "snmpd启动配置完毕"
		[ $? -eq 0 ] && /usr/local/etc/rc.d/snmpd restart && myfun $address '40' "snmpd已经运行" 
		echo "=========== $public Install Agent ==========" 
		#安装zabbix进度61-80%
		INSTALL_AGENT
		RC=/etc/rc.local
		SNMP2="/usr/local/etc/rc.d/snmpd start"
		[ -f $RC ]
		if [ $? -ne 0 ] ; then
			echo "#!/bin/sh" > $RC
		fi
		INIT
		echo "======= $public Delete down file ==========" 
                DELE
	;;
#ecool
	e )
		useradd -M -s /sbin/nologin zabbix
		if [ $? -eq 0 ]; then
			myfun $address '10' "zabbix用户创建完毕"
		else
			myfun $address '10' "zabbix用户已存在"
		fi 
		echo "=========== $public Download File ==========" 
		wget $url/client/snmpd.conf > /dev/null 2>&1 && myfun $address '20' "snmpd.conf配置文件下载完毕" 
		#下载文件在22-30%范围
                DOWN
		echo "=========== $public Install SNMP ============" 
		#snmp安装在31-40%
		SNMP
		echo "=========== $public Install Agent ==========" 
		#安装zabbix进度61-80%
		INSTALL_AGENT
		RC=/etc/rc.d/rc.local
		SNMP2="/usr/local/snmpd/sbin/snmpd -c /usr/local/snmpd/snmpd.conf"
		INIT
		echo "======= $public Delete down file ==========" 
                DELE
	;;
#suse
	s )
	    zypper install -y curl > /dev/null 2>&1
		zypper install -y wget > /dev/null 2>&1 && myfun $address '5' "wget安装完毕"
		zypper install -y gcc > /dev/null 2>&1 && myfun $address '15' "gcc安装完毕" 
		useradd -M -s /sbin/nologin zabbix
		if [ $? -eq 0 ];then
			myfun $address '18' "zabbix用户创建完毕"
		else
			myfun $address '18' "zabbix用户已存在"
		fi 
		echo "=========== $public Download File ==========" 
		#下载文件在22-30%范围
                DOWN
		echo "=========== $public Install SNMP ============" 
		#snmp安装在31-40%
		zypper install -y net-snmp > /dev/null 2>&1 && myfun $address '33' "snmp安装完毕" 
		[ $? -eq 0 ] && wget $url/client/snmpd.conf > /dev/null 2>&1 && myfun $address '35' "snmpd.conf配置文件下载完成" 
                [ $? -eq 0 ] && mv ./snmpd.conf /etc/snmp/snmpd.conf && myfun $address '37' "snmpd.conf配置文件已经替换" 
                [ $? -eq 0 ] && /etc/init.d/snmpd restart > /dev/null 2>&1 && myfun $address '38' "snmp启动完毕" 
                [ $? -eq 0 ] && chkconfig snmpd on && myfun $address '40' "已配置snmp开启启动" 
		echo "=========== $public Install Agent ==========" 
		#安装zabbix进度61-80%
		INSTALL_AGENT
		RC=/etc/init.d/after.local
		[ -f $RC ]
		if [ $? -ne 0 ] ; then
			echo "#!/bin/sh" > $RC
		fi
		INIT
		echo "======= $public Delete down file ==========" 
                DELE
	;;
esac
