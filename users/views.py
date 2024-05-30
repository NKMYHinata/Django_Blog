from random import randint
import re

from django.db import DatabaseError
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin

from libs.captcha.captcha import captcha
from libs.yuntongxun.sms import CCP
from users.models import User
from utils.response_code import RETCODE

import logging

logger = logging.getLogger('django')


# Create your views here.

# 定义注册视图
class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        """
        1. 接收数据
        2. 验证数据
            2.1 参数是否齐全
            2.2 手机号格式是否正确
            2.3 密码是否符合格式要求
            2.4 密码和确认密码是否一致
            2.5 验证短信验证码
        3. 保存注册信息
        4. 返回相应，跳转到指定页面

        :param request:
        :return:
        """
        # 1.接收数据
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        smscode = request.POST.get('sms_code')
        # 2.验证数据
        #     2.1 参数是否齐全
        if not all([mobile, password, password2, smscode]):
            return HttpResponseBadRequest('缺少必要的参数')
        #     2.2 手机号的格式是否正确
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('手机号不符合规则')
        #     2.3 密码是否符合格式
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseBadRequest('请输入8-20位密码，密码是数字，字母')
        #     2.4 密码和确认密码要一致
        if password != password2:
            return HttpResponseBadRequest('两次密码不一致')
        #     2.5 短信验证码是否和redis中的一致
        redis_conn = get_redis_connection('default')
        redis_sms_code = redis_conn.get('sms:%s' % mobile)
        if redis_sms_code is None:
            return HttpResponseBadRequest('短信验证码已过期')
        if smscode != redis_sms_code.decode():
            return HttpResponseBadRequest('短信验证码不一致')
        # 3.保存注册信息
        # create_user 可以使用系统的方法来对密码进行加密
        try:
            user = User.objects.create_user(username=mobile,
                                            mobile=mobile,
                                            password=password)
        except DatabaseError as e:
            logger.error(e)
            return HttpResponseBadRequest('注册失败')

        from django.contrib.auth import login
        # 状态保持
        login(request, user)
        # 4. 返回相应，跳转到指定页面
        # 暂时返回一个注册成功的信息，之后再实现跳转到指定页面
        # return HttpResponse('注册成功，重定向到首页')

        # redirect 进行重定向到首页
        # reverse 是可以通过namespace获取视图对应的路由
        response = redirect(reverse('home:index'))

        # 设置cookie信息，以方便首页中用户信息的判断与展示
        response.set_cookie('is_login', True)
        response.set_cookie('username', user.username, max_age=7 * 24 * 3600)

        return response


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


class SmsCodeView(View):

    def get(self, request):
        """
            1. 接收参数
            2. 参数验证
                2.1 参数是否齐全 (手机号, 图片验证码, uuid)
                2.2 验证图片验证码是否正确
                    2.2.1 从 redis 中检查验证码是否存在
                    2.2.2 若验证码存在，则获取后删除
                    2.2.3 比对验证码是否正确
            3. 生成短信验证码
            4. 将短信验证码保存到 redis 中
            5. 发送短信
            6. 返回相应

            :param request:
            return:
            """

        # 1
        mobile = request.GET.get('mobile')
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        # 2.1
        if not all([mobile, image_code, uuid]):
            return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必要参数'})

        # 2.2
        redis_conn = get_redis_connection('default')
        redis_img_code = redis_conn.get('img:%s' % uuid)

        # 2.2.1
        if redis_img_code is None:
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图片验证码已过期'})

        # 2.2.2
        try:
            redis_conn.delete('img:%s' % uuid)
        except Exception as e:
            logger.error(e)

        # 2.2.3
        if redis_img_code.decode().lower() != image_code.lower():
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图片验证码错误'})

        # 3
        sms_code = '%06d' % randint(0, 999999)
        # 为方便比对，将短信验证码记录到日志中
        logger.info(sms_code)

        # 4
        redis_conn.setex('sms:%s' % mobile, 300, sms_code)

        # 5
        CCP().send_template_sms(mobile, [sms_code, 5], 1)

        return JsonResponse({'code': RETCODE.OK, 'errmsg': '短信发送成功'})


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        """
        1. 接收参数
        2. 参数的验证
            2.1 验证手机号（符合规则）
            2.2 验证密码（符合规则）
        3. 用户认证登录
            采用系统自带的认证方法进行认证
            如果用户名密码正确则返回user
            如果用户名或密码不正确则返回None
        4. 状态保持
        5. 根据用户选择的是否记住登录状态进行判断
        6. 为首页显示设置cookie信息
        7. 返回相应
        :param request:
        :return:
        """
        # 1
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        # 2.1
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('手机号不符合规则')
        # 2.2
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return HttpResponseBadRequest('密码不符合要求')

        # 3
        from django.contrib.auth import authenticate
        # 默认的认证方法是进行username字段进行用户名的判断
        # 由于我们使用的是手机号，所以需要修改认证字段
        # 我们需要修改user模型，此处暂且保留
        user = authenticate(mobile=mobile, password=password)
        if user is None:
            return HttpResponseBadRequest('用户名或密码错误')

        # 4
        from django.contrib.auth import login
        login(request, user)

        next_page = request.GET.get('next')
        if next_page:
            response = redirect(next_page)
        else:
            response = redirect(reverse('home:index'))

        # 5+6
        if remember != 'on':  # 不记住登录状态
            # 0 表示浏览器关闭后会清除
            request.session.set_expiry(0)
            response.set_cookie("is_login", True)
            response.set_cookie('username', user.username, max_age=14 * 24 * 3600)
        else:
            # None 默认记住两周
            request.session.set_expiry(None)
            response.set_cookie('is_login', True, max_age=14 * 24 * 3600)
            response.set_cookie('username', user.username, max_age=14 * 24 * 3600)

        # 7
        return response


class LogoutView(View):

    def get(self, request):
        # 1. 进行session数据删除
        logout(request)
        # 2. 删除部分cookie数据
        response = redirect(reverse('home:index'))
        response.delete_cookie('is_login')
        # 3. 跳转首页
        return response


class ForgetPasswordView(View):
    def get(self, request):

        return render(request, 'forget_password.html')

    def post(self, request):
        """
        1. 接收数据
        2. 验证数据
            2.1 判断参数齐全
            2.2 手机号符合规则
            2.3 密码符合规则
            2.4 确认密码和确认密码是否一致
            2.5 判断短信验证码是否正确
        3. 根据手机号进行用户信息查询
        4. 如果手机号查询出用户信息，则进行密码修改
        5. 如果手机号没有查询出用户信息，则进行新用户的创建
        6. 跳转页面到登录页面
        7. 返回相应

        :param request:
        :return:
        """

        # 1
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        smscode = request.POST.get('sms_code')

        # 2.1
        if not all([mobile, password, password2, smscode]):
            return HttpResponseBadRequest('参数不全')

        # 2.2
        if not re.match(r'^1[3-9]\d{9}', mobile):
            return HttpResponseBadRequest('手机号不符合规则')

        # 2.3
        if not re.match(r'^[0-9A-Za-z]{8,20}', password):
            return HttpResponseBadRequest('密码不符合规则')

        # 2.4
        if password != password2:
            return HttpResponseBadRequest('密码不一致')

        # 2.5
        redis_conn = get_redis_connection('default')
        redis_sms_code = redis_conn.get('sms:%s' % mobile)
        if redis_sms_code is None:
            return HttpResponseBadRequest('短信验证码过期')
        if redis_sms_code.decode() != smscode:
            return HttpResponseBadRequest('短信验证码错误')

        # 3
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 5
            try:
                User.objects.create_user(username=mobile,
                                         mobile=mobile,
                                         password=password)
            except Exception:
                return HttpResponseBadRequest('修改失败，请稍后再试')
        else:
            # 4
            user.set_password(password)
            # 注意保存用户信息
            user.save()
        # 6
        response = redirect(reverse('users:login'))
        # 7
        return response


# 如果用户未登录，LoginRequiredMixin会进行默认跳转到accounts/login/?next=/center/
# 在setting中修改跳转页面
class UserCenterView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'center.html')
