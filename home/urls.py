from django.urls import path

from home.views import IndexView, DetailView
# from chat.views import

urlpatterns = [
    # 首页的路由
    path('', IndexView.as_view(), name='index'),

    # 详情页的路由
    path('detail/', DetailView.as_view(), name='detail'),
]
