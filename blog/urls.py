"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include
# 导入系统包
import logging
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

# 创建/获取日志器
logger = logging.getLogger('django')


# 使用日志器记录信息


def log(request):
    logger.info('info')

    return HttpResponse('test')


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', log),

    # include 参数中首先设置一个元组 urlconf_module, app_name
    # urlconf_module 设置子应用的路由
    # app_name 子应用名称
    # namespace 可以防止不同子应用之间的命名冲突
    path('', include(('users.urls', 'users'), namespace='users')),

    # 首页子应用路由
    path('', include(('home.urls', 'home'), namespace='home')),
]

# 追加图片访问路由
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
