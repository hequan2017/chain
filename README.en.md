[简体中文](README.md) | [English](README.en.md)

# Lianmiao CMDB (chain)

![LOGO](static/demo/LOGO.png)

![Python](https://img.shields.io/badge/Python-3.6-blue.svg)
![Django](https://img.shields.io/badge/Django-2.0-green.svg)
![Celery](https://img.shields.io/badge/Celery-4.2-brightgreen.svg)
![License](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)
![Maintained](https://img.shields.io/badge/Maintenance-Discontinued-red.svg)

> **⚠️ This project has been discontinued!** Due to personal workload, development ends here and no further updates or maintenance will be provided. Since the code has not been maintained for a long time, it may fail to deploy or contain bugs on different environments — please be aware. **For reference only.**

## 📖 Introduction

Lianmiao (chain) is a **Linux cloud host management system** built with Django. It combines CMDB asset management, WebSSH terminal login, batch command execution, asynchronous script execution, log tailing and scheduled tasks in a single console. Version v1.0.0 is the final release.

It targets small and medium-sized ops scenarios: hosts, credentials, batch operations and scheduled jobs are managed in one place, while django-guardian object permissions provide fine-grained authorization such as "assign assets by project".

On top of the original asset management, the project also adds container platform entries (Docker hosts / K8s clusters) and common query filters for the asset API.

## ✨ Features

- **Asset management (CMDB)**: host CRUD with intranet/external IP, OS version, CPU, memory, disk, bandwidth, platform, region, instance ID, etc.; one-click hardware info update and CSV export
- **Docker management**: maintain Docker host info (name, API endpoint, project/business, version, active status), under `Assets -> Docker Management`
- **K8s management**: maintain Kubernetes cluster info (cluster name, API server, default namespace, project/business, version, active status), under `Assets -> K8s Management`
- **WebSSH terminal**: browser SSH terminal built with Tornado + Paramiko (based on [huashengdun/webssh](https://github.com/huashengdun/webssh)); one-click login from the asset list, passwords stored with Fernet encryption
- **Command execution**: batch commands on assets via the built-in Ansible runner (tasks/ansible_2420)
- **Asynchronous script execution**: shell / python / yml scripts managed in a tool library, with persisted execution results
- **Variable groups**: define variable groups bound to assets for reusable batch task parameters
- **Log tailing**: follow remote server log output in real time
- **Scheduled tasks**: Celery + django-celery-beat with a visual console for Crontab / Interval schedules
- **Users / groups / permissions**: django-guardian object permissions combined with Django auth; five fine-grained permissions (view, add, change, delete, execute) plus login history
- **Asset API**: DRF list endpoint supporting `keyword` (fuzzy match on hostname/IP/project/business), `project`, `business`, `is_active` (true/false/1/0) filters, and `ordering` with an allowed-field whitelist (invalid values fall back to the default ordering)
- **Admin enhancements**: django-jet theme, pure-pagination, custom 404/500 pages

<details>
<summary>🔑 Permission model example (from the original README)</summary>

* Create an asset project [ops], an asset [web01] and an asset user [web01-root], assigned to the [ops] project
* Create a user [hequan] and add him to the user group [ops]
* System user - group object permission: add object type [Asset Project], project [ops], group [ops], permission [asset | Asset Project | View asset project]
* [hequan] then gets read access to [web01], [web01-root] and the [ops] project
* [admin] has all permissions by default; regular users cannot manage system users or the admin backend
* To let [hequan] add assets, tick "Can add asset" under System user - user or group

</details>

## 🛠 Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Python 3.6, Django 2.0.13, Django REST Framework 3.8.2, Celery 4.2.1 (django-celery-beat / django-celery-results), Channels 2.0 + Daphne, django-guardian 1.4.9, Ansible 2.6.3, Tornado 5.0 + Paramiko, Redis |
| Frontend | INSPINIA 2.7.1 template, Bootstrap, pyecharts |
| Database | SQLite3 (development; mysqlclient / PyMySQL included in requirements, can switch to MySQL seamlessly) |
| Tested on | Alibaba Cloud CentOS 7.5 |

## 🚀 Quick Start

```bash
git clone https://github.com/hequan2017/chain.git
```

Edit `chain/settings.py`:

```python
web_ssh = "47.104.140.38"    ## change to your public IP
web_port = 8002
```

Install system dependencies (CentOS 7):

```bash
mkdir /etc/ansible/
cd chain/

yum install sshpass bzip2 redis wget -y
systemctl start redis

# Build Twisted from source (if pip installation fails)
cd /tmp/
wget https://files.pythonhosted.org/packages/12/2a/e9e4fb2e6b2f7a75577e0614926819a472934b0b85f205ba5d5d2add54d0/Twisted-18.4.0.tar.bz2
tar xf Twisted-18.4.0.tar.bz2
cd Twisted-18.4.0
python3 setup.py install

pip3 install -r requirements.txt
```

Initialize and start:

```bash
cd chain/
python3 manage.py makemigrations
python3 manage.py migrate

# If you pulled the code with the Docker/K8s features, make sure to run migrations
python3 manage.py makemigrations asset
python3 manage.py migrate

# Create a superuser
python3 manage.py shell
from name.models import Names
user = Names.objects.create_superuser('admin', 'hequan@test.com', '1qaz.2wsx')
exit()

# Start the web service
python3 manage.py runserver 0.0.0.0:80

# Run in the background
nohup python36 manage.py runserver 0.0.0.0:8003 >> /tmp/chain-http.log 2>&1 &

# Start the WebSSH terminal service
python3 webssh/main.py

# Start Celery scheduled tasks
celery -B -A chain worker -l info
```

Troubleshooting:

```bash
# Error ImportError: No module named '_sqlite3'
yum -y install sqlite-devel
# then rebuild Python 3.6.5

# To run on Windows, comment out these two lines in tasks/views.py
# from tasks.ansible_2420.runner import AdHocRunner
# from tasks.ansible_2420.inventory import BaseInventory
```

## 📁 Directory Structure

![Project structure](static/demo/项目.png)

```text
├── asset       Assets (incl. asset API at asset/api/asset.html)
├── chain       Main configuration
├── crontab     Scheduled tasks
├── data        Test data / Dockerfile directory
├── index       Home page and user handling
├── tasks       Tasks (command/script execution, log tailing)
├── name        System users | groups | permissions
├── static      css | js
├── templates   HTML templates
└── webssh      SSH terminal in browser (based on https://github.com/huashengdun/webssh)
```

## 📸 Screenshots

![DEMO](static/demo/1.png)
![DEMO](static/demo/2.png)
![DEMO](static/demo/5.png)
![DEMO](static/demo/3.png)
![DEMO](static/demo/4.png)

## 🔗 Related Projects

Other ops projects by the same author (hequan2017):

- [autoops](https://github.com/hequan2017/autoops): Linux asset management (CMDB), WebSSH and an ops automation platform
- [cmdb](https://github.com/hequan2017/cmdb): asset management, host management, batch command/script execution, traffic graphs, WebSSH
- [husky](https://github.com/hequan2017/husky): a beginner-friendly Django CMDB tutorial project

## 📄 License

Licensed under the [Apache License 2.0](LICENSE).

## 💬 QQ Group

Group number: 620176501

<a target="_blank" href="//shang.qq.com/wpa/qunwpa?idkey=bbe5716e8bd2075cb27029bd5dd97e22fc4d83c0f61291f47ed3ed6a4195b024"><img border="0" src="https://github.com/hequan2017/cmdb/blob/master/static/img/group.png" alt="django开发讨论群" title="django开发讨论群"></a>
