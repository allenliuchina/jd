from django.shortcuts import render, redirect, reverse
from .models import GoodType, Good, Promotion, GoodComment
from django_redis import get_redis_connection


# Create your views here.


def list(request, id, num):
    type = GoodType.objects.get(pk=id)
    new_goods = Good.objects.filter(type=type).order_by('-create_time')
    goods = Good.objects.filter(type=type).order_by('-create_time')
    from django.core.paginator import Paginator
    paginator = Paginator(goods, 6)
    num = int(num)
    skus = paginator.page(num)
    conn = get_redis_connection()
    cart_key = 'cart_%s' % request.user.id
    goods = conn.hgetall(cart_key)
    cart_count = 0
    for v in goods.values():
        cart_count += int(v)

    return render(request, 'list.html',
                  {'type': type, 'skus_page': skus, 'new_skus': new_goods, 'cart_count': cart_count})


def detail(request, id):
    cart_count = 0
    if request.user.is_authenticated:
        conn = get_redis_connection()
        seen_good = 'seen_%s' % request.user.id
        cart_key = 'cart_%s' % request.user.id
        has_seen = conn.lrange(seen_good, 0, 5)
        if str(id).encode() not in has_seen:
            conn.lpush(seen_good, id)
        conn.ltrim(seen_good, 0, 4)
        goods = conn.hgetall(cart_key)

        cart_count = 0
        for v in goods.values():
            cart_count += int(v)

    good = Good.objects.get(pk=id)
    comments = GoodComment.objects.all()
    new_goods = Good.objects.filter(type=good.type).order_by('-create_time')[:2]
    return render(request, 'detail.html',
                  {'sku': good, 'comments': comments, 'new_goods': new_goods, 'cart_count': cart_count})


def index(request):
    if request.user.is_authenticated:
        conn = get_redis_connection()
        cart_key = 'cart_%s' % request.user.id
        goods = conn.hgetall(cart_key)
        cart_count = 0
        for v in goods.values():
            cart_count += int(v)
        types = GoodType.objects.all()
        u = Good.objects.first()
        promotion = Promotion.objects.all()
        context = {
            'types': types,
            'promotion': promotion,
            'cart_count': cart_count
        }

        return render(request, 'index.html', context)
    # 没有登录的话，直接返回生成的静态文件
    return redirect('/static/index.html')


from haystack.views import SearchView


class Search(SearchView):
    def extra_context(self):
        cart_count = 0
        if self.request.user.is_authenticated:
            conn = get_redis_connection()
            cart_key = 'cart_%s' % self.request.user.id
            goods = conn.hgetall(cart_key)
            cart_count = 0
            for v in goods.values():
                cart_count += int(v)
        context = {'cart_count':cart_count}
        return context
