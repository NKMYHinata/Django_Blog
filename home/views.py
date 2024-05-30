from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from home.models import ArticleCategory, Article, Comment
from django.http.response import HttpResponseNotFound
from django.core.paginator import Paginator, EmptyPage


# Create your views here.

class IndexView(View):
    def get(self, request):
        """
        1. 获取所有分类信息
        2. 接收用户点击的分类id
        3. 根据分类id进行分类的查询
        4. 获取分页参数
        5. 根据分类信息查询文章数据
        6. 创建分页器
        7. 进行分页处理
        8. 组织数据传递给模板

        :param request:
        :return:
        """

        # 1
        categories = ArticleCategory.objects.all()
        # 2
        cat_id = request.GET.get('cat_id', 1)
        # 3
        try:
            category = ArticleCategory.objects.get(id=cat_id)
        except ArticleCategory.DoesNotExist:
            return HttpResponseNotFound('没有此分类')

        # 4
        page_num = request.GET.get('page_num', 1)
        page_size = request.GET.get('page_size', 10)

        # 5
        articles = Article.objects.filter(category=category)

        # 6
        from django.core.paginator import Paginator, EmptyPage
        paginator = Paginator(articles, per_page=page_size)

        # 7
        try:
            page_articles = paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('empty page')
        # 总页数
        total_page = paginator.num_pages

        # 8
        context = {
            'categories': categories,
            'category': category,
            'articles': page_articles,
            'page_size': page_size,
            'total_page': total_page,
            'page_num': page_num
        }

        return render(request, 'index.html', context=context)


class DetailView(View):

    def get(self, request):
        """
        1. 接收文章id
        2. 根据文章id查询文章数据
        3. 查询分类数据

        5. 获取分页请求参数
        6. 根据文章信息查询评论
        7. 创建分页器
        8. 进行分页处理

        4. 组织模板数据

        :param request:
        :return:
        """

        # 1
        id = request.GET.get('id')

        # 2
        try:
            article = Article.objects.get(id=id)
        except Article.DoesNotExist:
            return render(request, '404.html')
        else:
            # 浏览量+1
            article.total_views += 1
            article.save()

        # 3
        categories = ArticleCategory.objects.all()

        # 查询浏览量最高的10个文章数据

        hot_articles = Article.objects.order_by('-total_views')[:9]

        # 5. 获取分页请求参数
        page_size = request.GET.get('page_size', 10)
        page_num = request.GET.get('page_num', 1)
        # 6. 根据文章信息查询评论
        comments = Comment.objects.filter(article=article).order_by('-created')
        # 获取评论总数
        total_count = comments.count()
        # 7. 创建分页器
        paginator = Paginator(comments, page_size)
        # 8. 进行分页处理
        try:
            page_comments = paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('empty page')
        # 获取总页数
        total_page = paginator.num_pages

        # 4
        context = {
            'categories': categories,
            'category': article.category,
            'article': article,
            'hot_articles': hot_articles,
            'total_count': total_count,
            'comments': page_comments,
            'page_size': page_size,
            'total_page': total_page,
            'page_num': page_num
        }

        return render(request, 'detail.html', context=context)

    def post(self, request):
        """
        1. 接收用户信息
        2. 判断用户是否登录
        3. 登录用户则可以接收from数组
            3.1 接收评论数据
            3.2 验证文章是否存在
            3.3 保存评论数据
            3.4 修改文章的评论数量
        4. 未登录的用户跳转到登录界面

        :param request:
        :return:
        """

        # 1
        user = request.user

        # 2
        if user and user.is_authenticated:
            # 3.1
            id = request.POST.get('id')
            content = request.POST.get('content')

            # 3.2
            try:
                article = Article.objects.get(id=id)
            except Article.DoesNotExist:
                return HttpResponseNotFound('没有此文章')

            # 3.3
            Comment.objects.create(
                content=content,
                article=article,
                user=user
            )

            # 3.4
            article.comments_count += 1
            article.save()

            # 刷新当前页面（重定向）
            path = reverse('home:detail') + '?id={}'.format(article.id)
            return redirect(path)
        else:
            # 4
            return redirect(reverse('users:login'))
