from django.db import models
from django.utils import timezone
from users.models import User
from django.utils import timezone


# Create your models here.

class ArticleCategory(models.Model):
    """
    文章分类
    """
    # 分类标题
    title = models.CharField(max_length=100, blank=True)
    # 分类创建时间
    created = models.DateTimeField(default=timezone.now())

    # admin站点显示，调试查看方便
    def __str__(self):
        return self.title

    class Meta:
        db_table = 'tb_category'  # 修改表名
        verbose_name = '类别管理'  # admin站点显示
        verbose_name_plural = verbose_name  #


# 文章模型
class Article(models.Model):
    # 1. 作者
    # 参数on_delete就是当user表中的数据删除之后，文章信息也同步删除
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 2. 标题图
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True)
    # 3. 标题
    title = models.CharField(max_length=20, blank=True)
    # 4. 栏目分类
    category = models.ForeignKey(ArticleCategory, null=True, blank=True, on_delete=models.CASCADE,
                                 related_name='article')
    # 5. 标签
    tags = models.CharField(max_length=20, blank=True)
    # 6. 摘要信息
    sumary = models.CharField(max_length=200, null=False, blank=False)
    # 7. 文章正文
    content = models.TextField()
    # 8. 浏览量
    total_views = models.PositiveSmallIntegerField(default=0)
    # 9. 评论量
    comments_count = models.PositiveSmallIntegerField(default=0)
    # 10.创建时间
    created = models.DateTimeField(default=timezone.now())
    # 11.修改时间
    update = models.DateTimeField(auto_now=True)

    # 修改表名以及admin展示的配置信息等
    class Mate:
        db_table = 'tb_article'
        ordering = ('-created',)
        verbose_name = '文章管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


# 评论模型
class Comment(models.Model):
    # 评论内容
    content = models.TextField()
    # 评论文章
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True)
    # 评论用户
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    # 评论时间
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.article.title

    class Meta:
        db_table = 'tb_comment'
        verbose_name = '评论管理'
        verbose_name_plural = verbose_name
