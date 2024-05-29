# 用于 users 子应用的视图路由
from django.urls import path
from users.views import RegisterView, ImageCodeView, SmsCodeView

# from users.views import ImageCodeView
# from users.views import SmsCodeView

app_name = 'users'

urlpatterns = [
    # path 的第一个参数：路由
    # path 的第二个参数：视图函数
    path('register/', RegisterView.as_view(), name='register'),

    # 图片验证码的路由
    path('imagecode/', ImageCodeView.as_view(), name='imagecode'),

    # 短信验证码路由
    path('smscode/', SmsCodeView.as_view(), name='smscode'),
]
