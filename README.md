## Chain

一个基于django2.0版本，极简主义的云主机CMDB增删改查项目！

非常适合django刚入门的人拿来参考！

大家可以看一下，欢迎提出修改意见 , 然后大家以此为基础,各自开发自己的板块，最后合成一个项目。


* 交流群号： 620176501    欢迎交流！

---
### DEMO



```bash
http://47.104.140.38:8001

账号 admin
密码 1qaz.2wsx

```

### 目录结构
  *  asset     资产
  *  chain     主配置目录
  *  data      测试数据/Dockerfile目录
  *  index     首页及用户处理
  *  tasks     任务
  *  static    静态任务
  *  templates 静态模板
  *  webssh    终端登录    利用的  https://github.com/huashengdun/webssh   此项目

###  环境


前端模板：
  * INSPINIA 2.7.1  

后端：
  * django==2.0.4
  * Python3.6.5   可参考 data/python3-install

数据库：
  * 目前开发阶段 用的 sqlite3,可无缝切换为 mysql



###  部署


修改 chain/settings.py



```bash
git clone https://github.com/hequan2017/chain.git
```

修改 chain/settings.py
```bash
web_ssh = "47.104.140.38"    ##修改为本机外网IP,
web_port = 8002
```




```bash
cd chain/

pip3   install -r   requirements.txt

mv     db.sqlite3  /tmp/

python3     manage.py   makemigrations
python3     manage.py   migrate

创建用户
python manage.py  shell  << EOF
from django.contrib.auth.models import User
user=User.objects.create_superuser('admin','emailname@demon.com','1qaz.2wsx')
exit()
EOF



python3   manage.py runserver 0.0.0.0:80


python3    webssh/main.py    ##启动终端登录功能

```

### docker部署

可以参考  data/dockerfile-*   文件部署

```bash
/opt
├── chain
├── dockerfile-chain
└── dockerfile-python3

docker bulid  -t python3.6.5  -f dockerfile-python3   .
docker bulid  -t chain  -f dockerfile-chain  .

docker  run -itd  --name chain   -p 8001:8001  -p 8002:8002     chain

docker  exec  -it   chain /bin/bash
```



```bash
如果遇到报错 ImportError: No module named '_sqlite3' ,可以执行下面的操作

yum -y install sqlite-devel

重新编译python3.6.4


想在windows 环境下运行，请注释 tasks/views.py  以下两行


from   .ansible_2420.runner import AdHocRunner
from   .ansible_2420.inventory import BaseInventory
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
