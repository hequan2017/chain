FROM   centos:7

RUN  yum   update    -y && \
     yum   install   iproute wget git  net-tools  gcc automake autoconf libtool make gcc gcc-c++   zlib*  python-devel mysql-devel zlib-devel openssl-devel  sqlite-devel  -y

WORKDIR  /usr/local/src
RUN  wget http://mirrors.sohu.com/python/3.6.5/Python-3.6.5.tgz  && tar xf Python-3.6.5.tgz
WORKDIR /usr/local/src/Python-3.6.5/

RUN ./configure   --enable-shared --enable-loadable-sqlite-extensions --with-zlib   && \
    make  -j  4  && make install  && \
    rm -rf /usr/bin/python   && \
    ln -s /usr/local/bin/python3.6    /usr/bin/python && \
    sed  -i    's/\#\!\/usr\/bin\/python/\#\!\/usr\/bin\/python2/'   /usr/bin/yum   && \
    sed  -i    's/\#\! \/usr\/bin\/python/\#\! \/usr\/bin\/python2/'   /usr/libexec/urlgrabber-ext-down  && \
    echo  "/usr/local/lib"  >> /etc/ld.so.conf  && \
    /sbin/ldconfig && \
    mkdir  -p  /root/.pip/ && \
    echo "[global]" >  /root/.pip/pip.conf  && \
    echo "trusted-host=mirrors.aliyun.com"  >>  /root/.pip/pip.conf  && \
    echo "index-url=http://mirrors.aliyun.com/pypi/simple/"  >>  /root/.pip/pip.conf && \
    python -V  && \
    rm -rf  /usr/local/src/Python-3.6.5*

WORKDIR  /tmp
RUN  wget https://mirrors.tuna.tsinghua.edu.cn/epel/epel-release-latest-7.noarch.rpm  && \
     rpm -ivh epel-release-latest-7.noarch.rpm   && \
     yum  install supervisor   redis sshpass  net-tools -y

WORKDIR  /usr/local/src

RUN wget http://download.redis.io/releases/redis-stable.tar.gz  && \
    tar -zxvf redis-stable.tar.gz   -C  /usr/local/   && \
    cd /usr/local/   && \
    mv redis-stable redis   && \
    cd redis   && \
    make

RUN git clone https://github.com/hequan2017/chain.git /opt/chain

WORKDIR   /opt/chain/

RUN  python -m pip  install -r   requirements.txt  && \
     python     manage.py   makemigrations  && \
     python     manage.py   migrate

RUN cp /opt/chain/data/password.sh /tmp/password.sh
RUN mkdir -p /etc/supervisor/ && cp /opt/chain/data/supervisord.conf /etc/supervisor/supervisord.conf

RUN   sed  -i "s/^web_ssh.*$/web_ssh = '${ip}' /g"  /opt/chain/chain/settings.py   && \
      sh /tmp/password.sh

RUN  sed  -i    's/\#\!\/usr\/bin\/python/\#\!\/usr\/bin\/python2/'   /usr/bin/supervisord  && \
     sed  -i    's/\#\!\/usr\/bin\/python/\#\!\/usr\/bin\/python2/'   /usr/bin/supervisorctl

EXPOSE  8001 8002
ENTRYPOINT ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
