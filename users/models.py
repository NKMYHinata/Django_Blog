from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class User(AbstractUser):
    # 定义手机号、头像和简介信息
    mobile = models.CharField(max_length=11, unique=True, blank=False)
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)
    user_desc = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = 'tb_user'  # 修改表明
        verbose_name = '用户管理'  # admin 后台显示
        verbose_name_plural = verbose_name  # admin 后台显示

    def __str__(self):
        return self.mobile
