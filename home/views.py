from django.shortcuts import render
from django.views import View
from home.models import ArticleCategory, Article
from django.http.response import HttpResponseNotFound


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

        # 4
        context = {
            'categories': categories,
            'category': article.category,
            'article': article,
            'hot_article': hot_articles
        }

        return render(request, 'detail.html', context)
