from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from libs.captcha.captcha import captcha


# Create your views here.

# 定义注册视图
class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')


class ImageCodeView(View):

    def get(self, request):
        """
        1. 接收前端传递的uuid
        2. 判断uuid是否成功获取
        3. 调用captcha生成图片验证码(图片二进制和验证码内容)
        4. 将uuid-验证码内容保存到redis中，设置过期时间
        5. 将图片二进制返回给前端

        :param request:
        :return:
        """

        uuid = request.GET.get('uuid')
        if uuid is None:
            return HttpResponseBadRequest('not found uuid')

        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection('default')
        # key, 过期时间, value
        redis_conn.setex('img:%s' % uuid, 300, text)
        return HttpResponse(image, content_type='image/jpeg')
