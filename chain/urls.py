"""chain URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from  index.views   import  index,login_view,logout,password_update,LoginHistorys

urlpatterns = [
    path('admin/', admin.site.urls,name='admin'),
    path('', index),
    path('index.html', index,name="index"),
    path('login.html',login_view),
    path('logout.html',logout),
    path('password_update.html',password_update,name="password_update"),
    path('index/login-history.html',LoginHistorys,name="login-history"),
    path('asset/', include('asset.urls', namespace="asset", ), ),
    path('tasks/', include('tasks.urls', namespace="tasks", ), ),

]


