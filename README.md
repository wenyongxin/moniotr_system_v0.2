#celery启动方式
celery worker -l INFO -A tasks.celery -B -Q for_add

更新celery启动方式
/usr/local/bin/python /usr/local/bin/celery worker -l INFO -A tasks.celery -B

监控系统开发

开发人员：温永鑫

用户管理模块：

用户创建管理
权限模板
URL目录管理


监控管理：

监控安装