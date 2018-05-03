## Chain

linux 云主机 管理系统，包含 CMDB,webssh登录、命令执行、异步执行shell/python/yml等。持续更新中。。。

非常适合django刚入门的人拿来参考！

大家可以看一下，欢迎提出修改意见 , 然后大家以此为基础,各自开发自己的板块，最后合成一个项目。


* 交流群号： 620176501    欢迎交流！

---
### DEMO



```bash
http://47.104.140.38:8001

账号  admin
密码  1qaz.2wsx

```

### 目录结构
  *  asset     资产
        * api   asset/api/asset.html
  *  chain     主配置目录
  *  data      测试数据/Dockerfile目录
  *  index     首页及用户处理
  *  tasks     任务
  *  static    css | js
  *  templates 静态模板
  *  webssh    终端登录     参考的  https://github.com/huashengdun/webssh   此项目

###  环境


前端模板：
  * INSPINIA 2.7.1  

后端：
  * django==2.0.4
  * Python 3.6.5

数据库：
  * 目前开发阶段 用的 sqlite3,可无缝切换为 mysql



###  部署


```bash
git clone https://github.com/hequan2017/chain.git
```


修改 chain/settings.py
```bash
web_ssh = "47.104.140.38"    ##修改为本机外网IP
web_port = 8002
```




```bash
mkdir /etc/ansible/
cd chain/

yum  install   sshpass   redis -y
systemctl start redis
pip3   install -r   requirements.txt



python3     manage.py   makemigrations
python3     manage.py   migrate



python manage.py  shell  << EOF
from django.contrib.auth.models import User
user=User.objects.create_superuser('admin','emailname@demon.com','1qaz.2wsx')
exit()
EOF




python3   manage.py runserver 0.0.0.0:80

python3    webssh/main.py    ##启动终端登录功能

python3   manage.py   celery worker     --loglevel=info

```



```bash
如果遇到报错 ImportError: No module named '_sqlite3' ,可以执行下面的操作

yum -y install sqlite-devel

重新编译python3.6.5

想在windows 环境下运行,请注释 tasks/views.py  以下两行


from   task.ansible_2420.runner import AdHocRunner
from   task.ansible_2420.inventory import BaseInventory


```

### docker部署

可以参考  data/dockerfile-*   文件部署

```bash
/opt
    chain
    password.sh
    dockerfile-chain
    dockerfile-python3


cd /opt
mv  /opt/chain/data/dockerfile-python3   .
mv  /opt/chain/data/dockerfile-chain   .
mv  /opt/chain/data/supervisord.conf  .
mv  /opt/chain/data/password.sh  .


修改password.sh 里面的密码



docker build  -t python3.6.5  -f dockerfile-python3    .
docker build  -t chain   -f dockerfile-chain  --build-arg  ip='47.104.140.38'  .

docker  run  -itd  --name chain   -p 8001:8001  -p 8002:8002    chain

docker  exec  -it   chain /bin/bash

```


###   截图
![DEMO](static/demo/1.png)
![DEMO](static/demo/2.png)
![DEMO](static/demo/3.png)
![DEMO](static/demo/4.png)

---
### 作者


#### 0.1
- 何全
