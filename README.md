## Chain

一个基于django2.0版本，极简主义的云主机CMDB增删改查项目！

非常适合django刚入门的人拿来参考！

---
### DEMO

```bash
http://47.94.252.25:8001

账号 admin
密码 1qaz.2wsx
```


###  环境

前端：INSPINIA 2.7.1  版本

后端：
 * django==2.0.3
 * django-bootstrap3
 * Python3.6.4


###  部署




```bash
git clone https://github.com/hequan2017/chain.git

cd chain

pip3 install -r requirements.txt
python3  manage.py   makemigrations
python3  manage.py   migrate

python3 manage.py createsuperuser

python3 manage.py runserver 0.0.0.0:80
```


```bash
如果遇到报错 ImportError: No module named '_sqlite3' ,可以执行下面的操作。

yum -y install sqlite-devel

安装python3.6.4 或者重新编译
```


###   截图
![DEMO](static/demo/1.png)
![DEMO](static/demo/2.png)
![DEMO](static/demo/3.png)

---
### 作者

#### 0.1
- 何全
